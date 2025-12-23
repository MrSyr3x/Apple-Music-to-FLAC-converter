"""
Apple Music platform handler
Uses gamdl for downloading with progress bars
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import Optional


def _get_url_type(url: str) -> str:
    """Detect the type of Apple Music URL."""
    if "/song/" in url:
        return "song"
    elif "/album/" in url:
        return "album"
    elif "/playlist/" in url:
        return "playlist"
    return "unknown"


def _create_progress_bar(percent: float, width: int = 25) -> str:
    """Create a visual progress bar."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def download_apple_music(
    url: str,
    cookies_path: Path,
    output_dir: Path,
    codec: str = "aac-legacy",
    include_lyrics: bool = True,
    flat_structure: bool = True
) -> bool:
    """
    Download from Apple Music with progress bars.
    """
    url_type = _get_url_type(url)
    
    # Build templates
    if url_type == "song":
        file_template = "{title}"
        folder_template = ""
    elif url_type == "playlist":
        file_template = "{title}"
        folder_template = "{playlist}"
    else:
        file_template = "{title}"
        folder_template = "{album}"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "gamdl",
        "--cookies-path", str(cookies_path),
        "--output-path", str(output_dir),
        "--song-codec", codec,
        "--playlist-file-template", file_template,
        "--single-disc-file-template", file_template,
        url
    ]
    
    if folder_template:
        cmd.extend(["--album-folder-template", folder_template])
    
    if not include_lyrics:
        cmd.append("--no-synced-lyrics")
    
    print("\n  📥 Downloading from Apple Music...\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        completed = 0
        current_song = None
        
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            
            # Parse gamdl output - various patterns
            # "Downloading: Song Name"
            if "Downloading" in line:
                match = re.search(r'Downloading[:\s]+(.+)', line)
                if match:
                    current_song = match.group(1).strip()
                    if len(current_song) > 50:
                        current_song = current_song[:47] + "..."
                    bar = _create_progress_bar(50)
                    print(f"\r  ⏳ {current_song:<50} [{bar}]  50%", end="", flush=True)
            
            # "Downloaded" or "Saved" or similar completion
            elif any(word in line for word in ["Downloaded", "Saved", "Done", "Finished"]):
                if current_song:
                    bar = _create_progress_bar(100)
                    print(f"\r  ✓ {current_song:<50} [{bar}] 100%")
                    completed += 1
                    current_song = None
            
            # Numbered list pattern "1. Song Name" or "01 Song Name"
            elif re.match(r'^\d+[\.\s]', line):
                match = re.search(r'^\d+[\.\s]+(.+)', line)
                if match:
                    song = match.group(1).strip()
                    if len(song) > 50:
                        song = song[:47] + "..."
                    bar = _create_progress_bar(100)
                    print(f"  ✓ {song:<50} [{bar}] 100%")
                    completed += 1
            
            # Progress percentage if shown
            elif "%" in line:
                match = re.search(r'(\d+)%', line)
                if match and current_song:
                    percent = int(match.group(1))
                    bar = _create_progress_bar(percent)
                    print(f"\r  ⏳ {current_song:<50} [{bar}] {percent:3d}%", end="", flush=True)
        
        process.wait()
        
        if completed > 0:
            print(f"\n  📊 Downloaded: {completed} songs\n")
        else:
            print()
        
        return process.returncode == 0
        
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("  ❌ gamdl not found")
        return False
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


def validate_apple_url(url: str) -> bool:
    """Check if URL is a valid Apple Music URL."""
    pattern = r'https?://(www\.)?music\.apple\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    return ["gamdl", "ffmpeg"]
