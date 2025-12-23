# 🎵 Music Downloader

A beautiful, user-friendly music downloader with support for **Apple Music**, **Spotify**, and **YouTube Music**.

![Platforms](https://img.shields.io/badge/Platforms-Apple%20Music%20%7C%20Spotify%20%7C%20YouTube-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ⚡ One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/MrSyr3x/Apple-Music-to-FLAC-converter/main/install.sh | bash
```

This will:
- Ask where you want to install
- Set up everything automatically
- Create a `music-dl` command for easy access
- Ask if you want to start now or later

## ✨ Features

- 🎨 **Interactive TUI** - No command-line knowledge needed
- 🍎 **Apple Music** - High-quality AAC/ALAC with lyrics
- 🎧 **Spotify** - Downloads via spotdl
- ▶️ **YouTube Music** - Direct downloads
- � **Custom Save Location** - SD card, external drive, anywhere!
- 🔄 **Auto Retry** - Failed songs retry via YouTube search
- 🔒 **Security First** - Option to delete cookies after download

## 🚀 Quick Start

### After Installation

```bash
music-dl
```

Or navigate to install folder:
```bash
./start.sh
```

### Manual Setup

```bash
git clone https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter.git
cd Apple-Music-to-FLAC-converter
./start.sh
```

## 🗑️ Uninstall

```bash
cd ~/music-downloader  # or your install path
./uninstall.sh
```

Downloads are kept safe during uninstall.

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

> 🔒 **Security**: Your cookies stay local. The app offers to delete them after download.

### 🎧 Spotify
Works with spotdl - just paste your URL:
- Tracks, albums, playlists all supported
- Downloads from YouTube with Spotify metadata
- Auto-retry for failed songs

### ▶️ YouTube Music
No login required! Just paste your URL.
- Works with any YouTube or YouTube Music URL
- Highest quality available

## 🎵 Audio Formats

Choose from 6 formats:

| Format | Quality | Best For |
|--------|---------|----------|
| **FLAC** | Lossless | Audiophiles |
| **MP3** | 320 kbps | Universal |
| **M4A** | 256 kbps | Apple devices |
| **WAV** | Lossless | Audio editing |
| **OGG** | Variable | Open source |
| **OPUS** | Best | Streaming |

## 📂 Smart Folder Structure

- **Single tracks** → `downloads/song.mp3`
- **Playlists** → `downloads/PlaylistName/song.mp3`
- **Albums** → `downloads/AlbumName/song.mp3`

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "FFmpeg not found" | Run `brew install ffmpeg` |
| Cookie not detected | Save with "cookie" in filename |
| Download fails | Check URL is valid |
| Some songs fail | Say "yes" to retry via YouTube |

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

- [gamdl](https://github.com/glomatico/gamdl) - Apple Music downloader
- [spotdl](https://github.com/spotDL/spotify-downloader) - Spotify downloader
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

---

<p align="center">
Made with ❤️ for music lovers
</p>
