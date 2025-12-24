# 🌊 Ripple

**Apple Music Downloader with Lossless Support**

Download your favorite songs, albums, and playlists from Apple Music in high-quality formats including lossless ALAC and FLAC.

## ⚡ Quick Install

```bash
curl -sL https://raw.githubusercontent.com/MrSyr3x/Apple-Music-to-FLAC-converter/main/install.sh | bash
```

Or manually:
```bash
git clone https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter.git
cd Apple-Music-to-FLAC-converter
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
./start.sh
```

## 🎵 Features

- **Lossless Audio**: AAC, ALAC, or FLAC
- **Full Metadata**: Album art, lyrics, track info
- **Progress Bars**: See download progress in real-time
- **Tab Completion**: Navigate paths easily

## 📋 Requirements

- Python 3.8+
- FFmpeg
- Apple Music cookies (for authentication)

## 🍪 Getting Cookies

1. Install browser extension: "Get cookies.txt LOCALLY"
2. Go to [music.apple.com](https://music.apple.com) and sign in
3. Export cookies as `cookies.txt`
4. Place in project folder or ~/Downloads

## 🎧 Format Options

| Format | Quality | Size |
|--------|---------|------|
| AAC | 256 kbps | ~7 MB/song |
| ALAC | Lossless | ~30 MB/song |
| FLAC | Lossless | ~35 MB/song |

## 📁 Downloads

Your music is saved to:
```
downloads/Apple Music/
```

## 🗑️ Uninstall

```bash
./uninstall.sh
```

---

Made with ❤️ for music lovers
