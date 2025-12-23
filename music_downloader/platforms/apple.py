"""
Apple Music platform handler
Uses gamdl for downloading
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def download_apple_music(
    url: str,
    cookies_path: Path,
    output_dir: Path,
    codec: str = "aac-legacy",
    include_lyrics: bool = True,
    flat_structure: bool = True
) -> bool:
    """
    Download from Apple Music using gamdl.
    
    Args:
        url: Apple Music URL
        cookies_path: Path to cookies.txt
        output_dir: Output directory
        codec: Audio codec (aac-legacy, alac, etc.)
        include_lyrics: Whether to download lyrics
        flat_structure: If True, use flat folder template
        
    Returns:
        True if successful, False otherwise
    """
    # Build template based on structure preference
    if flat_structure:
        template = "{title}"
    else:
        template = "{artist}/{title}"
    
    cmd = [
        sys.executable, "-m", "gamdl",
        "--cookies-path", str(cookies_path),
        "--output-path", str(output_dir),
        "--song-codec", codec,
        "--playlist-file-template", template,
        "--album-folder-template", template if flat_structure else "{album_artist}/{album}",
        "--single-disc-file-template", "{title}" if flat_structure else "{track:02d} {title}",
        url
    ]
    
    if not include_lyrics:
        cmd.append("--no-synced-lyrics")
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def validate_apple_url(url: str) -> bool:
    """Check if URL is a valid Apple Music URL."""
    import re
    pattern = r'https?://(www\.)?music\.apple\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    """Return list of required dependencies for Apple Music."""
    return ["gamdl", "ffmpeg"]
