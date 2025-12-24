# Ripple - Capabilities & Roadmap

## Current Capabilities

### Platforms Supported
| Platform | Formats | Source | Quality |
|----------|---------|--------|---------|
| **Apple Music** | AAC, ALAC, FLAC, MP3, OPUS, OGG | Apple CDN | ✅ True Lossless |
| **Spotify** | MP3, M4A, OPUS, OGG | YouTube | ⚠️ Lossy (max ~256kbps) |
| **YouTube Music** | MP3, M4A, OPUS, OGG | YouTube | ⚠️ Lossy (max ~256kbps) |

### Features We Have
- [x] Download tracks, albums, playlists from 3 platforms
- [x] Multiple format options (platform-appropriate)
- [x] Auto-retry failed downloads (3 attempts)
- [x] Failed song listing at end of download
- [x] Custom download location with tab completion
- [x] Cookie-based auth for Apple Music
- [x] Multi-download session for Apple Music
- [x] Metadata verification scan after downloads
- [x] **Rich progress bars** with visual display ✨
- [x] **Song names shown** during download ✨
- [x] **Colored output** (green=done, red=failed) ✨
- [x] **Download speed display** ✨
- [x] **ETA/Time elapsed** shown ✨
- [x] **Config system** (~/.ripple/config.json) ✨
- [x] **Remember last download location** ✨
- [x] Thumbnail cleanup after downloads
- [x] Lyrics file cleanup
- [x] Flatten folder structure option
- [x] Cookie file auto-detection

### Requirements
- Python 3.10+
- FFmpeg
- Apple Music cookies (for Apple Music only)
- No login needed for Spotify/YouTube

---

## Known Limitations

### Spotify/YouTube
- **No true FLAC** - Sources from YouTube, quality is lossy
- Max quality ~256kbps regardless of format selection

### Apple Music  
- Requires valid cookies from browser
- Cookies expire and need periodic refresh

---

## Future Improvements (Nice to Have)

### New Features
- [ ] True FLAC for Spotify (when viable API found)
- [ ] Batch download from text file
- [ ] Search by song name (without URL)
- [ ] Sync playlist (download new songs only)
- [ ] Download queue management
- [ ] Resume interrupted downloads
