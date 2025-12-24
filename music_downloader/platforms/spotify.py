"""
Spotify platform handler
Uses spotdl with auto-retry for failed downloads
"""

import asyncio
import subprocess
import sys
import re
import time
from pathlib import Path
from typing import Tuple, List


def _ensure_event_loop():
    """Fix for Python 3.14+."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def _get_url_type(url: str) -> str:
    """Detect the type of Spotify URL."""
    if "/track/" in url:
        return "track"
    elif "/album/" in url:
        return "album"
    elif "/playlist/" in url:
        return "playlist"
    return "unknown"


def _download_with_retry(cmd: list, max_retries: int = 3, retry_delay: int = 3) -> Tuple[int, List[str], int]:
    """
    Run spotdl with automatic retry for transient failures.
    Returns (completed_count, failed_songs, total_found)
    """
    failed_songs = []
    completed = 0
    total_found = 0
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**dict(__import__('os').environ), 'PYTHONUNBUFFERED': '1'}
    )
    
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue
        
        # Found song - count total
        if "Found" in line and "URL" in line:
            total_found += 1
            if total_found % 50 == 0:
                print(f"  🔍 Finding songs... {total_found} found", flush=True)
        
        # Download completed
        elif "Done" in line or "Downloaded" in line:
            completed += 1
            if completed <= 10 or completed % 10 == 0:
                if total_found > 0:
                    pct = int(completed / total_found * 100)
                    print(f"  ✓ Downloaded: {completed}/{total_found} ({pct}%)", flush=True)
                else:
                    print(f"  ✓ Downloaded: {completed}", flush=True)
        
        # Error - track for retry
        elif "Error" in line or "Unable" in line:
            match = re.search(r'"(.+?)"', line)
            if match:
                failed_songs.append(match.group(1))
    
    process.wait()
    return completed, failed_songs, total_found


def download_spotify(
    url: str,
    output_dir: Path,
    audio_format: str = "mp3",
    include_lyrics: bool = False
) -> Tuple[bool, List[str]]:
    """Download from Spotify with auto-retry for failures."""
    _ensure_event_loop()
    
    url_type = _get_url_type(url)
    
    if url_type == "track":
        template = "{title}.{ext}"
    elif url_type == "playlist":
        template = "{playlist}/{title}.{ext}"
    elif url_type == "album":
        template = "{album}/{title}.{ext}"
    else:
        template = "{artist}/{title}.{ext}"
    
    format_map = {"flac": "flac", "mp3": "mp3", "m4a": "m4a", "opus": "opus"}
    spotdl_format = format_map.get(audio_format, "mp3")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent.parent / "spotdl_wrapper.py"),
        url,
        "--output", str(output_dir),
        "-p", template,
        "--output-format", spotdl_format,
        "--download-threads", "4",
        "--search-threads", "4",
    ]
    
    print("\n  📥 Downloading from Spotify...")
    print("  (Large playlists may take a while - don't worry!)")
    print()
    
    try:
        # First attempt
        completed, failed_songs, total_found = _download_with_retry(cmd)
        
        # Auto-retry failed songs (up to 2 more attempts)
        retry_count = 0
        while failed_songs and retry_count < 2:
            retry_count += 1
            retry_count_display = len(failed_songs)
            print(f"\n  🔄 Retrying {retry_count_display} failed songs (attempt {retry_count + 1}/3)...")
            time.sleep(3)  # Wait before retry
            
            # Build retry URLs from song names
            # Re-run with same URL (spotdl will skip already downloaded)
            new_completed, still_failed, _ = _download_with_retry(cmd)
            completed += new_completed
            
            # Update failed list
            if len(still_failed) < len(failed_songs):
                # Some songs succeeded on retry
                recovered = len(failed_songs) - len(still_failed)
                print(f"  ✓ Recovered {recovered} songs on retry", flush=True)
            
            failed_songs = still_failed
            
            if not failed_songs:
                break
        
        print()
        print(f"  📊 Downloaded: {completed}, Failed: {len(failed_songs)}")
        print()
        
        return (True, failed_songs)
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}\n")
        return (False, [])


def validate_spotify_url(url: str) -> bool:
    """Check if URL is a valid Spotify URL."""
    pattern = r'https?://(open\.)?spotify\.com/(track|album|playlist|artist)/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    return ["spotdl", "ffmpeg"]
