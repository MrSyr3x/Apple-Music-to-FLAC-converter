# Ripple - Development Tracker

## UI Features
- [x] Rich progress bars with visual display
- [x] Song names shown during download
- [x] Colored output (green=done, yellow=downloading, red=failed)
- [x] Download speed display (songs/min)
- [x] ETA/Time elapsed shown
- [x] Failed songs shown immediately with **reason why**
- [x] Tab completion for file paths

## Features We Have
- [x] Download tracks, albums, playlists from 3 platforms
- [x] Apple Music: True lossless (AAC, ALAC, FLAC, MP3, OPUS, OGG)
- [x] Spotify: Best available (MP3, M4A, OPUS, OGG)
- [x] YouTube Music: Best available (MP3, M4A, OPUS, OGG)
- [x] **Platform-specific folders**: Spotify/, YouTube Music/, Apple Music/
- [x] Auto-retry failed downloads (3 attempts)
- [x] **Manual retry prompt**: Failed songs → "Retry via YouTube? (y/n)"
- [x] Custom download location with tab completion
- [x] Remember last download location
- [x] Cookie-based auth for Apple Music
- [x] Multi-download session for Apple Music
- [x] Metadata verification scan after downloads
- [x] Config system (~/.ripple/config.json)
- [x] Thumbnail cleanup after downloads
- [x] Lyrics file cleanup
- [x] **Playlist Analysis**
  - Duplicate detection
  - Missing songs detection (saves to MISSING_SONGS.txt)
  - Failed songs with reasons
  - Summary shows mismatch count

## In Progress / To Fix
- [ ] (None currently)

## Future Features (Maybe Later)
- [ ] True FLAC for Spotify (when viable API found)
- [ ] Batch download from text file
- [ ] Search by song name (without URL)
- [ ] Sync playlist (download new songs only)
- [ ] GUI version

## Bugs Raised & Fixed
| Bug | Status | Notes |
|-----|--------|-------|
| spotdl missing spotipy | ✅ Fixed | Reinstalled |
| Fake FLAC options | ✅ Fixed | Removed from menu |
| Failed songs not listed | ✅ Fixed | Shows name + reason |
| Missing songs not detected | ✅ Fixed | Uses count check + file |
| "All downloaded" when missing | ✅ Fixed | Count-based check |
