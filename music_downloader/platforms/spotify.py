"""
Spotify platform handler
Downloads by searching YouTube for the song (same method as spotDL/Telegram bots)
"""

import subprocess
import sys
import re
import json
from pathlib import Path
from typing import Optional, Tuple


def extract_spotify_info(url: str) -> Optional[Tuple[str, str]]:
    """
    Extract track/artist info from Spotify URL using yt-dlp's extractor.
    Returns (title, artist) or None if extraction fails.
    """
    try:
        # Use yt-dlp to extract info (it can read Spotify metadata)
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--dump-json",
                "--no-download",
                url
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            title = data.get("title", "")
            artist = data.get("artist", data.get("uploader", ""))
            if title:
                return (title, artist)
    except Exception:
        pass
    
    # Fallback: try to parse from URL structure or page
    return None


def search_youtube(query: str) -> Optional[str]:
    """
    Search YouTube for a song and return the first video URL.
    """
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                f"ytsearch1:{query}",
                "--get-url",
                "--no-playlist",
                "-f", "bestaudio"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Get the video ID instead
            result2 = subprocess.run(
                [
                    sys.executable, "-m", "yt_dlp",
                    f"ytsearch1:{query}",
                    "--get-id",
                    "--no-playlist"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result2.returncode == 0 and result2.stdout.strip():
                video_id = result2.stdout.strip()
                return f"https://www.youtube.com/watch?v={video_id}"
    except Exception:
        pass
    
    return None


def download_spotify(
    url: str,
    output_dir: Path,
    audio_format: str = "flac",
    include_lyrics: bool = True,
    flat_structure: bool = True
) -> bool:
    """
    Download from Spotify by searching YouTube.
    This is the same method used by spotDL and Telegram bots.
    
    Process:
    1. Extract song info from Spotify URL
    2. Search YouTube for the song
    3. Download from YouTube
    
    Args:
        url: Spotify URL
        output_dir: Output directory
        audio_format: Audio format (flac, mp3, m4a, wav, ogg, opus)
        include_lyrics: Not used (YouTube doesn't have synced lyrics)
        flat_structure: If True, download to flat structure
        
    Returns:
        True if successful, False otherwise
    """
    print("\n🔍 Extracting song info from Spotify...")
    
    # Try to extract song info
    info = extract_spotify_info(url)
    
    if info:
        title, artist = info
        search_query = f"{artist} - {title}" if artist else title
        print(f"   Found: {search_query}")
    else:
        # Fallback: try to extract from URL
        # Spotify URLs look like: /track/TRACKID or /album/ALBUMID
        match = re.search(r'/track/([a-zA-Z0-9]+)', url)
        if match:
            print("   ⚠️ Could not extract song info")
            print("   💡 Tip: Copy the song name and search on YouTube Music instead")
            return False
        else:
            print("   ⚠️ Only track URLs are supported for Spotify")
            print("   💡 For playlists/albums, use YouTube Music instead")
            return False
    
    print("🔍 Searching YouTube for this song...")
    youtube_url = search_youtube(search_query)
    
    if not youtube_url:
        print("   ❌ Could not find song on YouTube")
        print("   💡 Try searching manually on YouTube Music")
        return False
    
    print(f"   ✓ Found on YouTube")
    print("📥 Downloading...")
    
    # Build output template
    if flat_structure:
        template = "%(title)s.%(ext)s"
    else:
        template = "%(artist)s/%(title)s.%(ext)s"
    
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format", audio_format,
        "--audio-quality", "0",
        "--output", str(output_dir / template),
        "--embed-thumbnail",
        "--embed-metadata",
        youtube_url
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def validate_spotify_url(url: str) -> bool:
    """Check if URL is a valid Spotify URL."""
    pattern = r'https?://(open\.)?spotify\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    """Return list of required dependencies for Spotify."""
    return ["yt-dlp", "ffmpeg"]


def is_supported() -> bool:
    """Check if Spotify downloads are supported."""
    return True  # Now supported via YouTube search
