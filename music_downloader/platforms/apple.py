"""
Apple Music platform handler
Uses gamdl with live song counter
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


def download_apple_music(
    url: str,
    cookies_path: Path,
    output_dir: Path,
    codec: str = "aac-legacy",
    include_lyrics: bool = False,
    flat_structure: bool = True
) -> bool:
    """Download from Apple Music with live counter."""
    url_type = _get_url_type(url)
    
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
    
    print("\n  📥 Downloading from Apple Music...")
    print("  (This may take a while for large playlists)")
    print()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**dict(__import__('os').environ), 'PYTHONUNBUFFERED': '1'}
        )
        
        completed = 0
        total = 0
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
            
            # Track numbering (e.g., "01 Song Name" or "Downloading 1/50")
            if re.match(r'^\d+[\.\s/]', line):
                completed += 1
                # Show progress every song for first 10, then every 10
                if completed <= 10 or completed % 10 == 0:
                    print(f"  ✓ Downloaded: {completed}", flush=True)
            
            # Look for total count
            elif "total" in line.lower() or "tracks" in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    total = int(match.group(1))
                    print(f"  🔍 Found {total} tracks", flush=True)
            
            # Downloading indication
            elif "Downloading" in line or "Getting" in line:
                completed += 1
                if completed <= 10 or completed % 10 == 0:
                    if total > 0:
                        pct = int(completed / total * 100)
                        print(f"  ✓ Downloaded: {completed}/{total} ({pct}%)", flush=True)
                    else:
                        print(f"  ✓ Downloaded: {completed}", flush=True)
        
        process.wait()
        
        if completed > 0:
            print()
            print(f"  📊 Downloaded: {completed}")
            print()
        
        return True
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}\n")
        return False


def validate_apple_url(url: str) -> bool:
    """Check if URL is a valid Apple Music URL."""
    pattern = r'https?://(www\.)?music\.apple\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    return ["gamdl", "ffmpeg"]
