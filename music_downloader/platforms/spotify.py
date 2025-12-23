"""
Spotify platform handler

Note: Spotify uses DRM protection. Direct downloading is not possible.
This handler provides guidance to users about alternatives.
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
    Spotify download handler.
    
    Note: Spotify uses DRM protection, so direct download is not supported.
    This function will return False and the TUI will guide users to alternatives.
    
    The user should:
    1. Search for the song on YouTube Music
    2. Use the YouTube Music option instead
    
    Returns:
        False - direct Spotify download not supported
    """
    # Spotify uses DRM, cannot download directly
    # The spotdl library has Python 3.14 compatibility issues
    # and Spotify has cracked down on it anyway
    print("\n⚠️  Spotify uses DRM protection.")
    print("   Direct download is not currently supported.")
    print("\n💡 Try this instead:")
    print("   1. Find the song on YouTube Music")
    print("   2. Copy the YouTube Music URL")
    print("   3. Use the 'YouTube Music' option in this app")
    print()
    
    return False


def validate_spotify_url(url: str) -> bool:
    """Check if URL is a valid Spotify URL."""
    import re
    pattern = r'https?://(open\.)?spotify\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    """Return list of required dependencies for Spotify."""
    return ["ffmpeg"]


def is_supported() -> bool:
    """Check if Spotify downloads are supported."""
    return False  # Spotify DRM prevents direct downloads
