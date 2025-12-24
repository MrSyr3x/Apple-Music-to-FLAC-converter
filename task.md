# Ripple - Development Tracker

## UI Features
- [x] Rich progress bars with visual display
- [x] Song names shown during download
- [x] Colored output (green=done, yellow=downloading, red=failed)
- [x] Download speed display (songs/min)
- [x] ETA/Time elapsed shown
- [x] Failed songs listed at end with names
- [x] Tab completion for file paths

## Features We Have
- [x] Download tracks, albums, playlists from 3 platforms
- [x] Apple Music: True lossless (AAC, ALAC, FLAC, MP3, OPUS, OGG)
- [x] Spotify: Best available (MP3, M4A, OPUS, OGG)
- [x] YouTube Music: Best available (MP3, M4A, OPUS, OGG)
- [x] Auto-retry failed downloads (3 attempts)
- [x] Custom download location with tab completion
- [x] Remember last download location
- [x] Cookie-based auth for Apple Music
- [x] Multi-download session for Apple Music
- [x] Metadata verification scan after downloads
- [x] Config system (~/.ripple/config.json)
- [x] Thumbnail cleanup after downloads
- [x] Lyrics file cleanup
- [x] **Playlist Analysis** (new!)
  - Duplicate detection
  - Missing songs detection
  - Failed songs tracking
  - Summary with counts

## In Progress / To Fix
- [ ] (None currently)

## Future Features (Maybe Later)
- [ ] True FLAC for Spotify (when viable API found)
- [ ] Batch download from text file
- [ ] Search by song name (without URL)
- [ ] Sync playlist (download new songs only)
- [ ] Download queue management
- [ ] Resume interrupted downloads
- [ ] GUI version

## Bugs Raised & Fixed
| Bug | Status | Notes |
|-----|--------|-------|
| spotdl missing spotipy dependency | ✅ Fixed | Reinstalled spotipy |
| Fake FLAC options for Spotify | ✅ Fixed | Removed FLAC/WAV from Spotify/YouTube |
| Failed songs not listed | ✅ Fixed | Added failed song names display |
| Missing songs check not working | ✅ Fixed | Now uses spotipy API directly |
| No duplicate detection | ✅ Fixed | Added find_duplicates function |
