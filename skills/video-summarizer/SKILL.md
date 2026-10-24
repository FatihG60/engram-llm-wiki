---
name: video-summarizer
description: >-
  Summarize videos the user provides (YouTube/Shorts/Instagram/TikTok/X URLs or local
  .mp4/.mkv/.webm files). Downloads with yt-dlp, transcribes speech with faster-whisper
  (GPU when available, CPU int8 fallback), and builds timestamped frame contact sheets so
  the agent can actually "watch" the video and ingest it into the Second Brain.
---

# Video Summarizer Skill

Turns any video into **transcript + metadata + timestamped frame contact sheets** (`4x2` grids), ready to be summarized by your agent and ingested into your Obsidian LLM Wiki + Engram database.

## 1. Run the pipeline

```bash
python skills/video-summarizer/scripts/prepare_video.py "<URL-or-path>" --lang auto
```

| Flag | Default | Description |
|---|---|---|
| `--lang tr` / `en` / `auto` | `auto` | Force language if auto-detect is uncertain |
| `--model small` / `medium` / `large-v3` | `small` | Whisper model size |
| `--interval N` | auto (~32 frames) | Seconds between extracted video frames |
| `--no-frames` / `--no-audio` | off | Skip frames for podcasts or audio for silent screen captures |
| `--out DIR` | `~/.gemini/antigravity/video-summaries/<name>` | Custom output directory |

## 2. Read the outputs & Ingest into the Wiki

1. Read `meta.json` and `transcript_timed.txt`.
2. View each `frames/sheet_XX.png` image to read on-screen code, slides, diagrams, and benchmarks.
3. Synthesize a structured note in your Obsidian Vault, link it to the relevant MOC, run `engram_log`, and run `engram_sync` so the transcript and summary are indexed in `engram.db`.
