"""
YouTube Music platform handler  
Uses yt-dlp for downloading with progress bars
Crops thumbnails to square to remove letterbox bars
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import Optional


def _get_url_type(url: str) -> str:
    """Detect the type of YouTube URL."""
    if "list=" in url:
        return "playlist"
    elif "playlist" in url:
        return "playlist"
    elif "/album/" in url:
        return "album"
    else:
        return "video"


def _create_progress_bar(percent: float, width: int = 25) -> str:
    """Create a visual progress bar."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def download_youtube(
    url: str,
    output_dir: Path,
    audio_format: str = "flac",
    flat_structure: bool = True
) -> bool:
    """
    Download from YouTube/YouTube Music with progress bars.
    Crops thumbnails to square format to remove letterbox bars.
    """
    url_type = _get_url_type(url)
    
    # Template based on URL type
    if url_type == "video":
        template = "%(title)s.%(ext)s"
    else:
        template = "%(playlist)s/%(title)s.%(ext)s"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format", audio_format,
        "--audio-quality", "0",
        "--output", str(output_dir / template),
        # Thumbnail handling - convert to jpg and crop to square
        "--embed-thumbnail",
        "--convert-thumbnails", "jpg",
        # FFmpeg post-processor to crop thumbnail to square (center crop)
        "--ppa", "ThumbnailsConvertor:-vf crop=w='min(iw,ih)':h='min(iw,ih)'",
        "--embed-metadata",
        "--add-metadata",
        "--concurrent-fragments", "3",
        "--progress",
        "--newline",
        "--no-warnings",
        url
    ]
    
    print("\n  📥 Downloading from YouTube...\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        current_song = None
        completed = 0
        current_percent = 0
        last_song_printed = None
        
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            
            # Parse download destination (new song starting)
            if "[download] Destination:" in line:
                match = re.search(r'Destination:\s*(.+)', line)
                if match:
                    filename = Path(match.group(1)).stem
                    # Clean up filename
                    if len(filename) > 50:
                        filename = filename[:47] + "..."
                    current_song = filename
                    current_percent = 0
            
            # Parse download progress percentage
            elif "[download]" in line and "%" in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match and current_song:
                    current_percent = float(match.group(1))
                    bar = _create_progress_bar(current_percent)
                    # Print on same line (overwrite)
                    print(f"\r  ⏳ {current_song:<50} [{bar}] {current_percent:5.1f}%", end="", flush=True)
            
            # Parse completion
            elif "[ExtractAudio]" in line and current_song:
                if current_song != last_song_printed:
                    bar = _create_progress_bar(100)
                    print(f"\r  ✓ {current_song:<50} [{bar}] 100.0%")
                    completed += 1
                    last_song_printed = current_song
                    current_song = None
            
            # Already downloaded
            elif "has already been downloaded" in line:
                match = re.search(r'\[download\]\s*(.+?)\s+has already', line)
                if match:
                    name = Path(match.group(1)).stem
                    if len(name) > 50:
                        name = name[:47] + "..."
                    bar = _create_progress_bar(100)
                    print(f"  ✓ {name:<50} [{bar}] (cached)")
                    completed += 1
        
        process.wait()
        
        print(f"\n  📊 Downloaded: {completed} songs\n")
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


def validate_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL."""
    patterns = [
        r'https?://(www\.)?youtube\.com/.+',
        r'https?://(www\.)?youtu\.be/.+',
        r'https?://music\.youtube\.com/.+',
    ]
    return any(re.match(p, url) for p in patterns)


def get_required_dependencies() -> list:
    return ["yt-dlp", "ffmpeg"]
