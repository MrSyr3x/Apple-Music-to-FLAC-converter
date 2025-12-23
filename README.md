# 🍎 Apple Music to FLAC

A beautiful command-line tool to download Apple Music playlists, albums, and songs in high quality, with optional FLAC conversion.

![CLI Demo](https://raw.githubusercontent.com/MrSyr3x/Apple-Music-to-FLAC-converter/main/demo.gif)

## ✨ Features

- 🎵 **High-Quality Audio** - Download in AAC 256kbps or Apple Lossless (ALAC)
- 🔄 **FLAC Conversion** - Automatically convert to FLAC format
- 📁 **Smart Organization** - Files saved in folders named after playlists
- 🎨 **Beautiful CLI** - Colorful output with progress indicators
- 🔒 **Secure** - Your credentials stay local on your machine

## 📋 Requirements

- **Python 3.10+**
- **FFmpeg** - For audio conversion
- **Apple Music Subscription** - Active subscription required

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter.git
cd Apple-Music-to-FLAC-converter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Your Cookies (One-time Setup)

This tool needs your Apple Music cookies to authenticate. Your cookies stay **local on your machine** and are never shared.

<details>
<summary><b>🍎 Safari (macOS)</b></summary>

Safari doesn't support cookie export extensions. **Easiest solution:** Use Chrome or Firefox just for the one-time cookie export.

**Alternative: Export manually via macOS Keychain**
1. Open **Keychain Access** app
2. Search for "music.apple.com"
3. This method is complex - we recommend just using Chrome/Firefox for the cookie export step

**Or use a Python script:**
```bash
# Install the tool
pip install safari-cookies-export

# Export cookies (Safari must be closed)
python -m safari_cookies_export music.apple.com > cookies.txt
```

</details>

<details>
<summary><b>🌐 Chrome / Edge / Brave</b></summary>

1. Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to [music.apple.com](https://music.apple.com) and log in
3. Click extension icon → Export
4. Save as `cookies.txt` in the project folder

</details>

<details>
<summary><b>🦊 Firefox</b></summary>

1. Install [Export Cookies](https://addons.mozilla.org/addon/export-cookies-txt)
2. Go to [music.apple.com](https://music.apple.com) and log in
3. Click extension icon → Export
4. Save as `cookies.txt` in the project folder

</details>

### 3. Download Music!

```bash
# Download a playlist
python download.py "https://music.apple.com/us/playlist/your-playlist"

# Download and convert to FLAC
python download.py --flac "https://music.apple.com/us/playlist/your-playlist"

# Download an album
python download.py --flac "https://music.apple.com/us/album/album-name/123456789"
```

## 📖 Usage

```
python download.py [OPTIONS] URL

Options:
  -f, --format    Audio format: aac-legacy (default), aac-he-legacy, alac
  --flac          Convert to FLAC after download
  --check         Verify all dependencies are installed
  --setup         Show cookie setup instructions
  -h, --help      Show help message
```

### Examples

```bash
# Standard quality (AAC 256kbps)
python download.py "https://music.apple.com/us/playlist/..."

# Convert to FLAC
python download.py --flac "https://music.apple.com/us/playlist/..."

# Download all albums from an artist
python download.py --flac "https://music.apple.com/us/artist/artist-name/123456"

# Check if everything is set up correctly
python download.py --check
```

## 📂 Output Structure

```
downloads/
└── Playlist Name/
    ├── 01 Song Title.flac
    ├── 02 Song Title.flac
    ├── 03 Song Title.flac
    └── ...
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "cookies.txt not found" | Run `python download.py --setup` for instructions |
| "FFmpeg not found" | Install FFmpeg: `brew install ffmpeg` (macOS) |
| Download fails | Your cookies may have expired - re-export them |
| "No audio files found" | Check if the URL is valid and accessible |

## 🎧 About Audio Quality

| Format | Quality | Notes |
|--------|---------|-------|
| `aac-legacy` | 256 kbps | Default, widely compatible |
| `aac-he-legacy` | 64 kbps | Smaller files, lower quality |
| `alac` | Lossless | Requires additional setup |

> **Note**: Converting AAC to FLAC changes the container format but doesn't improve audio quality. For true lossless, you need ALAC source (requires wrapper setup - see [gamdl docs](https://github.com/glomatico/gamdl)).

## 🛡️ Privacy & Security

- ✅ Your cookies are stored **locally** on your machine
- ✅ No data is sent to any third-party servers
- ✅ Each user uses their **own** Apple Music subscription
- ❌ Never share your `cookies.txt` file with anyone

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

- [gamdl](https://github.com/glomatico/gamdl) - The amazing Apple Music downloader library
- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

---

<p align="center">
  Made with ❤️ for the Apple Music community
</p>
