# 🎵 Music Downloader

A beautiful, user-friendly music downloader with support for **Apple Music**, **Spotify**, and **YouTube Music**.

![Platforms](https://img.shields.io/badge/Platforms-Apple%20Music%20%7C%20Spotify%20%7C%20YouTube-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🎨 **Interactive TUI** - No command-line knowledge needed
- 🍎 **Apple Music** - High-quality AAC/ALAC with lyrics
- 🎧 **Spotify** - Downloads without login
- ▶️ **YouTube Music** - Downloads without login
- 🔄 **FLAC Conversion** - Automatic lossless conversion
- 📁 **Smart Organization** - Flat or artist-folder structure
- 🍪 **Auto Cookie Detection** - Finds your cookies automatically
- 🔒 **Security First** - Option to delete cookies after download

## 🚀 Quick Start

### One-Click Method

```bash
git clone https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter.git
cd Apple-Music-to-FLAC-converter
./start.sh
```

That's it! The script handles everything automatically.

### Manual Setup

```bash
# Clone and setup
git clone https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter.git
cd Apple-Music-to-FLAC-converter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python download.py
```

## 📋 Requirements

- **Python 3.10+**
- **FFmpeg** - Install with `brew install ffmpeg`

## 🎵 Platform Guide

### 🍎 Apple Music
Requires cookies (one-time setup):

1. Install browser extension:
   - **Chrome**: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - **Firefox**: [Export Cookies](https://addons.mozilla.org/addon/export-cookies-txt)
2. Go to [music.apple.com](https://music.apple.com) and log in
3. Export cookies (save anywhere - we'll find it!)
4. Run the app and select your cookie file

> 🔒 **Security**: Your cookies stay local. The app offers to delete them after download for extra safety.

### ▶️ YouTube Music ⭐ Recommended
No login required! Just paste your URL and download.
- Works with any YouTube or YouTube Music URL
- Highest quality available
- Includes metadata and thumbnails

### 🎧 Spotify ⚠️ Limited Support
> **Note**: Spotify uses DRM protection. Direct downloads are **not currently supported**.
> 
> **Workaround**: Search for your song on YouTube Music and use that URL instead.

## 📂 Output Options

**Flat structure (default):**
```
downloads/
├── Song Name.flac
├── Another Song.flac
└── ...
```

**With artist folders:**
```
downloads/
└── Artist Name/
    ├── Song Name.flac
    └── ...
```

## 🎧 Audio Quality

| Platform | Quality | Format |
|----------|---------|--------|
| Apple Music | 256 kbps AAC | .m4a → .flac |
| Spotify | ~320 kbps | .flac |
| YouTube | Variable | .flac |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "FFmpeg not found" | Run `brew install ffmpeg` |
| Cookie not detected | Save with "cookie" in filename |
| Download fails | Check URL is valid and accessible |

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

- [gamdl](https://github.com/glomatico/gamdl) - Apple Music downloader
- [spotdl](https://github.com/spotDL/spotify-downloader) - Spotify downloader
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [InquirerPy](https://github.com/kazhala/InquirerPy) - Interactive prompts

---

<p align="center">
Made with ❤️ for music lovers
</p>
