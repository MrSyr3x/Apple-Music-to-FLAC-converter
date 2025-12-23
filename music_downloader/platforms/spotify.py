"""
Spotify platform handler
Uses spotdl for downloading
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def download_spotify(
    url: str,
    output_dir: Path,
    audio_format: str = "flac",
    include_lyrics: bool = True,
    flat_structure: bool = True
) -> bool:
    """
    Download from Spotify using spotdl.
    
    Args:
        url: Spotify URL
        output_dir: Output directory
        audio_format: Audio format (flac, mp3, etc.)
        include_lyrics: Whether to download lyrics
        flat_structure: If True, download to flat structure
        
    Returns:
        True if successful, False otherwise
    """
    # Build output template
    if flat_structure:
        template = "{title}"
    else:
        template = "{artist}/{title}"
    
    cmd = [
        sys.executable, "-m", "spotdl",
        "--output", str(output_dir / f"{template}.{audio_format}"),
        "--format", audio_format,
        url
    ]
    
    if include_lyrics:
        cmd.extend(["--lyrics", "synced"])
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def validate_spotify_url(url: str) -> bool:
    """Check if URL is a valid Spotify URL."""
    import re
    pattern = r'https?://(open\.)?spotify\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    """Return list of required dependencies for Spotify."""
    return ["spotdl", "ffmpeg"]
