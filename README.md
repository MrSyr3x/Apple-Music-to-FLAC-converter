# 🌊 Ripple

A beautiful music downloader for **Spotify**, **YouTube Music**, and **Apple Music**.

## ⚡ Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/MrSyr3x/ripple/main/install.sh | bash
```

## ✨ Features

- 🎨 **Beautiful TUI** - No commands to memorize
- 🎧 **Spotify** - Tracks, albums, playlists
- ▶️ **YouTube Music** - Direct downloads
- 🍎 **Apple Music** - With cookies
- 📁 **Custom Location** - Save anywhere
- 🔄 **Auto Retry** - Failed songs retry via YouTube
- 📊 **Verification** - Checks artwork & metadata

## 📋 Requirements

### 🍎 macOS
```bash
brew install ffmpeg python
```

### 🪟 Windows
```bash
# Using winget
winget install ffmpeg python

# Or using chocolatey
choco install ffmpeg python
```

### 🐧 Linux
C'mon, you're on Linux... do I really have to tell you, my Linux geek buddy? 😎

```bash
# You already know:
sudo apt install ffmpeg python3
# or
sudo pacman -S ffmpeg python
# etc.
```

## 🚀 Usage

After installation:
```bash
ripple        # Use the global command
# or
./start.sh   # From install directory
```

## 🎵 Formats

| Format | Size/song | Best for |
|--------|-----------|----------|
| MP3 | ~4 MB | Universal |
| OPUS | ~2 MB | Smallest |
| OGG | ~3 MB | Open |
| M4A | ~4 MB | Apple |
| FLAC | ~25 MB | Lossless |
| WAV | ~40 MB | Editing |

## 🍪 Apple Music Setup

**Chrome/Firefox only** (Safari is a headache, trust me):

1. Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to music.apple.com → Log in
3. Click extension → Export
4. Run Ripple → Select the file

## 📂 Output Structure

```
downloads/
├── Single Track.mp3           # Single songs
├── Playlist Name/             # Playlists
│   ├── Song 1.mp3
│   └── Song 2.mp3
└── Album Name/                # Albums
    ├── Track 1.mp3
    └── Track 2.mp3
```

## 🗑️ Uninstall

```bash
./uninstall.sh
```

Your downloaded music is kept safe.

## 🙏 Credits

- [spotdl](https://github.com/spotDL/spotify-downloader)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [gamdl](https://github.com/glomatico/gamdl)

---

<p align="center">
Made with 🌊 for music lovers
</p>
