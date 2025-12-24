"""
YouTube Music platform handler  
Uses yt-dlp with progress bars
"""

import subprocess
import sys
import re
from pathlib import Path


def _get_url_type(url: str) -> str:
    """Detect the type of YouTube URL."""
    if "list=" in url:
        return "playlist"
    elif "playlist" in url:
        return "playlist"
    else:
        return "video"


def download_youtube(
    url: str,
    output_dir: Path,
    audio_format: str = "mp3",
    flat_structure: bool = True
) -> bool:
    """Download from YouTube/YouTube Music with progress."""
    url_type = _get_url_type(url)
    
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
        "--embed-thumbnail",
        "--embed-metadata",
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
            bufsize=1,
            env={**dict(__import__('os').environ), 'PYTHONUNBUFFERED': '1'}
        )
        
        current_song = None
        completed = 0
        last_percent = -1
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
            
            # New song starting
            if "[download] Destination:" in line:
                match = re.search(r'Destination:\s*(.+)', line)
                if match:
                    filename = Path(match.group(1)).stem
                    if len(filename) > 35:
                        filename = filename[:32] + "..."
                    current_song = filename
                    last_percent = -1
            
            # Download progress percentage
            elif "[download]" in line and "%" in line and "ETA" in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match and current_song:
                    pct = float(match.group(1))
                    # Only update every 5%
                    if pct - last_percent >= 5 or pct >= 100:
                        last_percent = pct
                        bar_len = 20
                        filled = int(bar_len * pct / 100)
                        bar = "█" * filled + "░" * (bar_len - filled)
                        print(f"\r  ⏳ {current_song:<35} [{bar}] {pct:5.1f}%", end="", flush=True)
            
            # 100% complete
            elif "[download] 100%" in line and current_song:
                bar = "█" * 20
                print(f"\r  ⏳ {current_song:<35} [{bar}] 100.0%", end="", flush=True)
            
            # ExtractAudio means conversion done
            elif "[ExtractAudio]" in line and current_song:
                bar = "█" * 20
                print(f"\r  ✓ {current_song:<35} [{bar}] done   ")
                completed += 1
                current_song = None
            
            # Already downloaded
            elif "has already been downloaded" in line:
                match = re.search(r'\[download\]\s*(.+?)\s+has already', line)
                if match:
                    name = Path(match.group(1)).stem
                    if len(name) > 35:
                        name = name[:32] + "..."
                    print(f"  ✓ {name:<35} [cached]")
                    completed += 1
        
        process.wait()
        
        print(f"\n  📊 Downloaded: {completed}\n")
        
        return True
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}\n")
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
