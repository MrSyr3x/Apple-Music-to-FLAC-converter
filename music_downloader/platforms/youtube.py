"""
YouTube Music platform handler
Uses yt-dlp with Rich progress display
"""

import subprocess
import sys
import re
import time
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None


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
    """Download from YouTube/YouTube Music with rich progress."""
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
    
    if RICH_AVAILABLE:
        console.print("\n  [bold]📥 Downloading from YouTube...[/bold]\n")
    else:
        print("\n  📥 Downloading from YouTube...\n")
    
    start_time = time.time()
    
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
        
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=25),
                TaskProgressColumn(),
                TextColumn("•"),
                TimeElapsedColumn(),
                console=console,
                transient=False
            ) as progress:
                
                download_task = progress.add_task("[yellow]Starting...", total=100)
                
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # New song starting
                    if "[download] Destination:" in line:
                        match = re.search(r'Destination:\s*(.+)', line)
                        if match:
                            filename = Path(match.group(1)).stem
                            if len(filename) > 40:
                                filename = filename[:37] + "..."
                            current_song = filename
                            progress.update(download_task, completed=0, description=f"[yellow]⬇ {current_song}")
                            last_percent = -1
                    
                    # Download progress percentage
                    elif "[download]" in line and "%" in line:
                        match = re.search(r'(\d+\.?\d*)%', line)
                        if match:
                            pct = float(match.group(1))
                            progress.update(download_task, completed=pct)
                    
                    # ExtractAudio means conversion done
                    elif "[ExtractAudio]" in line and current_song:
                        progress.update(download_task, completed=100, description=f"[green]✓ {current_song}")
                        completed += 1
                        current_song = None
                    
                    # Already downloaded
                    elif "has already been downloaded" in line:
                        match = re.search(r'\[download\]\s*(.+?)\s+has already', line)
                        if match:
                            name = Path(match.group(1)).stem
                            if len(name) > 40:
                                name = name[:37] + "..."
                            progress.update(download_task, completed=100, description=f"[dim]⏭ {name} (cached)")
                            completed += 1
                    
                    # Error - show failed song immediately
                    elif "ERROR:" in line or "error:" in line.lower():
                        if current_song:
                            console.print(f"\n  [red]✗ Failed: {current_song}[/red]")
                        else:
                            # Try to extract what failed
                            console.print(f"\n  [red]✗ Error: {line[:60]}[/red]")
        else:
            # Fallback without Rich
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line:
                    continue
                
                if "[download] Destination:" in line:
                    match = re.search(r'Destination:\s*(.+)', line)
                    if match:
                        current_song = Path(match.group(1)).stem[:35]
                        last_percent = -1
                
                elif "[download]" in line and "%" in line and "ETA" in line:
                    match = re.search(r'(\d+\.?\d*)%', line)
                    if match and current_song:
                        pct = float(match.group(1))
                        if pct - last_percent >= 5 or pct >= 100:
                            last_percent = pct
                            bar_len = 20
                            filled = int(bar_len * pct / 100)
                            bar = "█" * filled + "░" * (bar_len - filled)
                            print(f"\r  ⏳ {current_song:<35} [{bar}] {pct:5.1f}%", end="", flush=True)
                
                elif "[ExtractAudio]" in line and current_song:
                    print(f"\r  ✓ {current_song:<35} [done]      ")
                    completed += 1
                    current_song = None
                
                elif "has already been downloaded" in line:
                    completed += 1
                
                elif "ERROR:" in line or "error:" in line.lower():
                    if current_song:
                        print(f"\n  ✗ Failed: {current_song}", flush=True)
                    else:
                        print(f"\n  ✗ Error: {line[:60]}", flush=True)
        
        process.wait()
        
        # Summary with speed
        elapsed = time.time() - start_time
        
        if RICH_AVAILABLE:
            console.print(f"\n  [bold green]📊 Downloaded: {completed} songs[/bold green]")
            if completed > 0 and elapsed > 0:
                speed = completed / elapsed * 60
                console.print(f"  [dim]Speed: {speed:.1f} songs/min • Time: {elapsed:.0f}s[/dim]\n")
        else:
            print(f"\n  📊 Downloaded: {completed}")
            if completed > 0 and elapsed > 0:
                speed = completed / elapsed * 60
                print(f"  Speed: {speed:.1f} songs/min • Time: {elapsed:.0f}s\n")
        
        return True
        
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n  [yellow]⚠ Download cancelled by user[/yellow]\n")
        else:
            print("\n  ⚠ Download cancelled by user\n")
        return False
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n  [red]❌ Error: {e}[/red]\n")
        else:
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
