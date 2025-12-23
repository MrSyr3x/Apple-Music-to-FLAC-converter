"""
Spotify platform handler
Uses spotdl with progress bars and clean output
"""

import asyncio
import subprocess
import sys
import re
from pathlib import Path
from typing import Tuple, List


def _ensure_event_loop():
    """Fix for Python 3.14+: Ensure an event loop exists."""
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
    elif "/artist/" in url:
        return "artist"
    return "unknown"


def _create_progress_bar(percent: float, width: int = 25) -> str:
    """Create a visual progress bar."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def download_spotify(
    url: str,
    output_dir: Path,
    audio_format: str = "flac",
    include_lyrics: bool = True,
    flat_structure: bool = True
) -> Tuple[bool, List[str]]:
    """
    Download from Spotify with progress bars.
    """
    _ensure_event_loop()
    
    url_type = _get_url_type(url)
    
    # Build template
    if url_type == "track":
        template = "{title}.{ext}"
    elif url_type == "playlist":
        template = "{playlist}/{title}.{ext}"
    elif url_type == "album":
        template = "{album}/{title}.{ext}"
    else:
        template = "{artist}/{title}.{ext}"
    
    format_map = {
        "flac": "flac", "mp3": "mp3", "m4a": "m4a",
        "wav": "wav", "ogg": "ogg", "opus": "opus"
    }
    spotdl_format = format_map.get(audio_format, "flac")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent.parent / "spotdl_wrapper.py"),
        url,
        "--output", str(output_dir),
        "-p", template,
        "--output-format", spotdl_format,
        "--download-threads", "1",
        "--search-threads", "2",
    ]
    
    if include_lyrics:
        cmd.extend(["--lyrics-provider", "genius"])
    
    failed_songs = []
    completed = 0
    total = 0
    
    print("\n  📥 Downloading from Spotify...\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        current_song = None
        
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            
            # Parse "Found YouTube URL" (counting total songs)
            if "Found YouTube URL for" in line:
                total += 1
                match = re.search(r'Found YouTube URL for "(.+?)"', line)
                if match:
                    song = match.group(1)
                    if len(song) > 50:
                        song = song[:47] + "..."
                    print(f"  🔍 Found: {song}")
            
            # Parse progress lines with percentage
            # spotdl shows: "Song Name    Done   ━━━━━━━ 100%"
            elif "%" in line and ("Done" in line or "Error" in line):
                # Extract song name and status
                match = re.search(r'^(.+?)\s+(Done|Error)\s+', line)
                if match:
                    song = match.group(1).strip()
                    status = match.group(2)
                    
                    if len(song) > 50:
                        song = song[:47] + "..."
                    
                    bar = _create_progress_bar(100)
                    
                    if status == "Done":
                        completed += 1
                        print(f"  ✓ {song:<50} [{bar}] 100%")
                    else:
                        failed_songs.append(song)
                        print(f"  ✗ {song:<50} [{bar}] failed")
            
            # Parse error messages
            elif "Error" in line and ("While" in line or "Converting" in line):
                match = re.search(r'While.*:\s*(.+)', line)
                if match:
                    failed_songs.append(match.group(1).strip())
            
            elif "Unable to get audio stream" in line:
                match = re.search(r'"(.+?)"\s+by\s+"(.+?)"', line)
                if match:
                    failed_songs.append(f"{match.group(2)} - {match.group(1)}")
        
        process.wait()
        
        print(f"\n  📊 Downloaded: {completed}, Failed: {len(failed_songs)}\n")
        
        return (True, failed_songs)
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return (False, failed_songs)


def validate_spotify_url(url: str) -> bool:
    """Check if URL is a valid Spotify URL."""
    pattern = r'https?://(open\.)?spotify\.com/(track|album|playlist|artist)/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    return ["spotdl", "ffmpeg"]


def is_supported() -> bool:
    return True
