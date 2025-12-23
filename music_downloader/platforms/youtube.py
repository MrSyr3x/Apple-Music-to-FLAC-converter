"""
YouTube Music platform handler  
Uses yt-dlp for downloading
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def download_youtube(
    url: str,
    output_dir: Path,
    audio_format: str = "flac",
    flat_structure: bool = True
) -> bool:
    """
    Download from YouTube/YouTube Music using yt-dlp.
    
    Args:
        url: YouTube URL
        output_dir: Output directory
        audio_format: Audio format (flac, mp3, etc.)
        flat_structure: If True, download to flat structure
        
    Returns:
        True if successful, False otherwise
    """
    # Build output template
    if flat_structure:
        template = "%(title)s.%(ext)s"
    else:
        template = "%(artist)s/%(title)s.%(ext)s"
    
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format", audio_format,
        "--audio-quality", "0",  # Best quality
        "--output", str(output_dir / template),
        "--embed-thumbnail",
        "--embed-metadata",
        url
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def validate_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL."""
    import re
    patterns = [
        r'https?://(www\.)?youtube\.com/.+',
        r'https?://(www\.)?youtu\.be/.+',
        r'https?://music\.youtube\.com/.+',
    ]
    return any(re.match(p, url) for p in patterns)


def get_required_dependencies() -> list:
    """Return list of required dependencies for YouTube."""
    return ["yt-dlp", "ffmpeg"]
