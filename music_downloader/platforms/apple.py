"""
Apple Music platform handler
Uses gamdl with Rich progress display
"""

import subprocess
import sys
import re
import time
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None


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
    """Download from Apple Music with rich progress display."""
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
    
    if RICH_AVAILABLE:
        console.print("\n  [bold]📥 Downloading from Apple Music...[/bold]")
        console.print("  [dim](This may take a while for large playlists)[/dim]\n")
    else:
        print("\n  📥 Downloading from Apple Music...")
        print("  (This may take a while for large playlists)\n")
    
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
        
        completed = 0
        total = 0
        current_song = None
        
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
                
                download_task = progress.add_task("[cyan]Starting...", total=None)
                
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Track total count
                    if "total" in line.lower() or "tracks" in line.lower():
                        match = re.search(r'(\d+)', line)
                        if match:
                            total = int(match.group(1))
                            progress.update(download_task, total=total, description=f"[cyan]Found {total} tracks")
                    
                    # Downloading indication
                    elif "Downloading" in line or "Getting" in line:
                        match = re.search(r'"(.+?)"', line)
                        if match:
                            current_song = match.group(1)
                            if len(current_song) > 40:
                                current_song = current_song[:37] + "..."
                        progress.update(download_task, description=f"[yellow]⬇ {current_song or 'track'}")
                    
                    # Track numbering completed
                    elif re.match(r'^\d+[\.\s/]', line):
                        completed += 1
                        progress.update(download_task, completed=completed, description=f"[green]✓ {current_song or 'track'}")
                    
                    # Decrypting/processing
                    elif "Decrypting" in line or "Remuxing" in line:
                        progress.update(download_task, description=f"[blue]🔓 Processing...")
                    
                    # Any success indication
                    elif "Success" in line or "Saved" in line:
                        completed += 1
                        progress.update(download_task, completed=completed, description=f"[green]✓ {current_song or 'Saved'}")
                    
                    # Error - show failed track immediately
                    elif "Error" in line or "error" in line.lower():
                        if current_song:
                            console.print(f"\n  [red]✗ Failed: {current_song}[/red]")
                        else:
                            console.print(f"\n  [red]✗ Error: {line[:60]}[/red]")
                    
                    # No downloadable media - cookies issue
                    elif "No downloadable" in line or "skipping" in line.lower():
                        if current_song:
                            console.print(f"\n  [red]✗ Failed: {current_song}[/red]")
                            console.print(f"    [dim]Reason: Not available (check cookies/subscription)[/dim]")
        else:
            # Fallback without Rich
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line:
                    continue
                
                if re.match(r'^\d+[\.\s/]', line):
                    completed += 1
                    if completed <= 10 or completed % 10 == 0:
                        print(f"  ✓ Downloaded: {completed}", flush=True)
                
                elif "total" in line.lower() or "tracks" in line.lower():
                    match = re.search(r'(\d+)', line)
                    if match:
                        total = int(match.group(1))
                        print(f"  🔍 Found {total} tracks", flush=True)
                
                elif "Downloading" in line or "Getting" in line:
                    completed += 1
                    if completed <= 10 or completed % 10 == 0:
                        if total > 0:
                            pct = int(completed / total * 100)
                            print(f"  ✓ Downloaded: {completed}/{total} ({pct}%)", flush=True)
                        else:
                            print(f"  ✓ Downloaded: {completed}", flush=True)
                
                elif "Error" in line or "Failed" in line or "error" in line.lower():
                    print(f"\n  ✗ Error: {line[:60]}", flush=True)
        
        process.wait()
        
        # Summary with speed
        elapsed = time.time() - start_time
        
        if completed > 0:
            if RICH_AVAILABLE:
                console.print(f"\n  [bold green]📊 Downloaded: {completed} songs[/bold green]")
                if elapsed > 0:
                    speed = completed / elapsed * 60
                    console.print(f"  [dim]Speed: {speed:.1f} songs/min • Time: {elapsed:.0f}s[/dim]\n")
            else:
                print(f"\n  📊 Downloaded: {completed}")
                if elapsed > 0:
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


def validate_apple_url(url: str) -> bool:
    """Check if URL is a valid Apple Music URL."""
    pattern = r'https?://(www\.)?music\.apple\.com/.+'
    return bool(re.match(pattern, url))


def get_required_dependencies() -> list:
    return ["gamdl", "ffmpeg"]
