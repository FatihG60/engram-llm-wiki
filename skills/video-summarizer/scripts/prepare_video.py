"""Prepare a video (local file or URL) for summarization by an agent.

Steps:
  1. If input is a URL, download it with yt-dlp (also grabs title/description).
  2. Extract mono 16 kHz audio with ffmpeg and transcribe it with faster-whisper.
  3. Extract frames and tile them into contact sheets (PNG) the agent can view.
  4. Write transcript.txt, transcript_timed.txt, meta.json and a manifest.

Usage:
  python prepare_video.py <path-or-url> [--out DIR] [--lang tr|en|auto]
                          [--model small|medium|large-v3] [--interval SEC]
                          [--no-frames] [--no-audio]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def slug(text: str, n: int = 60) -> str:
    s = re.sub(r"[^\w\-]+", "_", text, flags=re.UNICODE).strip("_")
    return s[:n] or "video"


def ensure_tool(name: str, hint: str) -> None:
    if not shutil.which(name):
        sys.exit(f"[!] '{name}' not found. {hint}")


def download(url: str, out: Path) -> tuple[Path, dict]:
    ytdlp = shutil.which("yt-dlp")
    base = [ytdlp] if ytdlp else [sys.executable, "-m", "yt_dlp"]
    if shutil.which("node"):
        base += ["--js-runtimes", "node"]
    meta = {}
    r = run(base + ["--dump-single-json", "--no-playlist", url])
    if r.returncode == 0:
        j = json.loads(r.stdout)
        meta = {k: j.get(k) for k in ("title", "uploader", "channel", "upload_date",
                                       "duration", "view_count", "like_count",
                                       "description", "webpage_url", "tags")}
    r = run(base + ["--no-playlist", "-f", "bv*[height<=720]+ba/b[height<=720]/b",
                    "--merge-output-format", "mp4", "-o", str(out / "video.%(ext)s"), url])
    if r.returncode != 0:
        sys.exit(f"[!] yt-dlp failed:\n{r.stderr[-2000:]}")
    vids = sorted(out.glob("video.*"))
    if not vids:
        sys.exit("[!] Download produced no file.")
    return vids[0], meta


def probe_duration(video: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(video)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def transcribe(video: Path, out: Path, lang: str, model: str) -> str:
    wav = out / "audio.wav"
    r = run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    if r.returncode != 0 or not wav.exists():
        return "(no audio track)"
    import numpy as np
    from faster_whisper import WhisperModel

    with wave.open(str(wav)) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0

    device, ctype = "cpu", "int8"
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            device, ctype = "cuda", "float16"
    except Exception:
        pass
    try:
        m = WhisperModel(model, device=device, compute_type=ctype)
        segs, info = m.transcribe(audio, language=None if lang == "auto" else lang, vad_filter=True)
        segs = list(segs)
    except Exception:  # CUDA libs missing etc. -> CPU fallback
        m = WhisperModel(model, device="cpu", compute_type="int8")
        segs, info = m.transcribe(audio, language=None if lang == "auto" else lang, vad_filter=True)
        segs = list(segs)

    plain = " ".join(s.text.strip() for s in segs)
    timed = "\n".join(f"[{int(s.start)//60:02d}:{int(s.start)%60:02d}] {s.text.strip()}" for s in segs)
    (out / "transcript.txt").write_text(plain, encoding="utf-8")
    (out / "transcript_timed.txt").write_text(timed, encoding="utf-8")
    wav.unlink(missing_ok=True)
    return f"lang={info.language} ({info.language_probability:.2f}), {len(segs)} segments"


def frames(video: Path, out: Path, duration: float, interval: float | None) -> list[str]:
    fdir = out / "frames"
    fdir.mkdir(exist_ok=True)
    if not interval:
        # aim for ~24-48 frames total regardless of length
        interval = max(2.0, round(duration / 32, 1)) if duration else 5.0
    font = ""
    for f in (r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if Path(f).exists():
            font = "fontfile='" + f.replace("\\", "/").replace(":", "\\:") + "':"
            break
    vf = f"fps=1/{interval},scale=360:-2,drawtext={font}text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=4x2"
    r = run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", vf, str(fdir / "sheet_%02d.png")])
    if r.returncode != 0:  # drawtext may be unavailable -> retry without timestamps
        vf = f"fps=1/{interval},scale=360:-2,tile=4x2"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", vf, str(fdir / "sheet_%02d.png")])
    return [str(p) for p in sorted(fdir.glob("sheet_*.png"))]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out")
    ap.add_argument("--lang", default="auto")
    ap.add_argument("--model", default="small")
    ap.add_argument("--interval", type=float)
    ap.add_argument("--no-frames", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    a = ap.parse_args()

    ensure_tool("ffmpeg", "Install: winget install Gyan.FFmpeg")
    is_url = bool(re.match(r"https?://", a.source))
    name = slug(a.source.split("/")[-1].split("?")[0] if is_url else Path(a.source).stem)
    out = Path(a.out) if a.out else Path.home() / ".gemini" / "antigravity" / "video-summaries" / name
    out.mkdir(parents=True, exist_ok=True)

    meta: dict = {}
    if is_url:
        video, meta = download(a.source, out)
    else:
        video = Path(a.source)
        if not video.exists():
            sys.exit(f"[!] File not found: {video}")
        meta = {"title": video.stem}

    meta["duration"] = meta.get("duration") or probe_duration(video)
    meta["video_path"] = str(video)
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    tinfo = "skipped" if a.no_audio else transcribe(video, out, a.lang, a.model)
    sheets = [] if a.no_frames else frames(video, out, meta["duration"], a.interval)

    manifest = {
        "out_dir": str(out),
        "meta": str(out / "meta.json"),
        "transcript": str(out / "transcript.txt") if (out / "transcript.txt").exists() else None,
        "transcript_timed": str(out / "transcript_timed.txt") if (out / "transcript_timed.txt").exists() else None,
        "transcription_info": tinfo,
        "frame_sheets": sheets,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
