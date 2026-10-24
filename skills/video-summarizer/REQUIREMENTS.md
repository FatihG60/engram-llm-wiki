# 📦 Video Summarizer — Paketler, İndirme Bağlantıları ve Kurulum Rehberi (Dependencies & Links)

Bu dosya `video-summarizer` yeteneğinin kullandığı 3 ana aracın (**`yt-dlp`**, **`FFmpeg`**, **`faster-whisper`**) resmi indirme bağlantılarını ve tek satırlık kurulum komutlarını içerir.

---

## 🔗 1. Resmi Proje ve İndirme Bağlantıları (Official Links)

| Araç / Paket | Görevi | Resmi GitHub / Web Sayfası | Doğrudan İndirme / Paket Sayfası |
|---|---|---|---|
| **1. `yt-dlp`** | 1.800+ siteden video ve metaveri indirici | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | [GitHub Releases (`yt-dlp.exe`)](https://github.com/yt-dlp/yt-dlp/releases/latest) · [PyPI: `yt-dlp`](https://pypi.org/project/yt-dlp/) |
| **2. `FFmpeg`** | Videodan ses ayıklama (`16kHz WAV`) ve `4x2` zaman damgalı kare tabakası (`sheet_XX.png`) üretimi | [ffmpeg.org](https://ffmpeg.org/) | [ffmpeg.org/download.html](https://ffmpeg.org/download.html) · [Gyan.dev Windows Builds](https://www.gyan.dev/ffmpeg/builds/) · [BtbN GitHub Releases](https://github.com/BtbN/FFmpeg-Builds/releases) |
| **3. `faster-whisper`** | CTranslate2 tabanlı yerel, hızlı yapay zeka konuşma tanıma (Speech-to-Text) motoru | [github.com/SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | [PyPI: `faster-whisper`](https://pypi.org/project/faster-whisper/) |
| **4. `CTranslate2`** | `faster-whisper` için GPU (CUDA) ve CPU (`int8`) hızlandırma motoru | [github.com/OpenNMT/CTranslate2](https://github.com/OpenNMT/CTranslate2) | [PyPI: `ctranslate2`](https://pypi.org/project/ctranslate2/) |
| **5. `Node.js` *(Opsiyonel)*** | YouTube SABR / `n-challenge` imzalarını çözerken `yt-dlp` tarafından JS çalışma zamanı olarak kullanılır | [nodejs.org](https://nodejs.org/) | [nodejs.org/en/download](https://nodejs.org/en/download) |

---

## ⚡ 2. Hızlı Kurulum Komutları (Quick Installation)

### 🪟 Windows (PowerShell)
```powershell
# 1. FFmpeg kurulumu (Winget ile sistem PATH'ine otomatik eklenir)
winget install Gyan.FFmpeg

# 2. Python paketlerinin (yt-dlp, faster-whisper, numpy) tek komutla kurulumu
python -m pip install -U -r requirements.txt

# (Opsiyonel) YouTube JS challenge çözümü için Node.js
winget install OpenJS.NodeJS.LTS
```

### 🍎 macOS (Homebrew)
```bash
# 1. FFmpeg kurulumu
brew install ffmpeg

# 2. Python paketlerinin kurulumu
pip3 install -U -r requirements.txt
```

### 🐧 Linux (Ubuntu / Debian)
```bash
# 1. FFmpeg kurulumu
sudo apt update && sudo apt install -y ffmpeg

# 2. Python paketlerinin kurulumu
pip3 install -U -r requirements.txt
```

---

## 🎮 3. GPU (NVIDIA CUDA) Desteği Hakkında Not
- `faster-whisper`, sistemde NVIDIA ekran kartı ve CUDA kütüphaneleri varsa **otomatik olarak `cuda` (`float16`)** modunda çalışır.
- Eğer GPU veya CUDA bulunamazsa hata vermez; **otomatik olarak `cpu` (`int8`)** moduna düşerek her bilgisayarda sorunsuz çalışır.
