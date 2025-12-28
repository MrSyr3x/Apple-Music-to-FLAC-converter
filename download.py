#!/usr/bin/env python3
"""
🍎 Apple Music to FLAC (Ripple v3.1 Rebuilt)
"""

import sys
import shutil
import subprocess
from pathlib import Path

# Import TUI components
from tui import (
    console, 
    print_banner, 
    print_success, 
    print_error, 
    print_info,
    print_warning,
    select_format, 
    select_cookies_file, 
    get_url,
    destroy_cookies_option
)

def check_dependencies() -> bool:
    """Check if external dependencies are installed."""
    missing = []
    
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    
    # Check gamdl
    try:
        subprocess.run([sys.executable, "-m", "gamdl", "--help"], capture_output=True)
    except Exception:
        missing.append("gamdl")
        
    if missing:
        print_error(f"Missing dependencies: {', '.join(missing)}")
        if "ffmpeg" in missing:
            print_info("Install FFmpeg: brew install ffmpeg")
        if "gamdl" in missing:
            print_info("Install gamdl: pip install gamdl")
        return False
        
    return True

def strip_track_number(filename: str) -> str:
    """
    Remove track number prefix from filename.
    Examples:
    - "01 Song Name.m4a" → "Song Name.m4a"
    - "1-05 Song Name.flac" → "Song Name.flac"
    - "05 Song.m4a" → "Song.m4a"
    """
    import re
    # Match patterns like "01 ", "1-05 ", "05-", etc.
    cleaned = re.sub(r'^(\d+[-\s])+', '', filename)
    return cleaned if cleaned else filename

def move_new_files(temp_dir: Path, target_dir: Path, already_moved: set, include_lrc: bool = True) -> list:
    """
    Move any new audio and optionally .lrc files from temp to target directory.
    Strips track number prefixes from filenames.
    
    Args:
        include_lrc: If True, move .lrc files too. If False, only audio files.
    """
    import shutil
    
    audio_extensions = ['.m4a', '.flac', '.mp3', '.opus', '.aac']
    if include_lrc:
        all_extensions = audio_extensions + ['.lrc']
    else:
        all_extensions = audio_extensions
    
    newly_moved = []
    
    for ext in all_extensions:
        for file in temp_dir.rglob(f'*{ext}'):
            if str(file) in already_moved:
                continue
            
            # Strip track number prefix from filename
            clean_name = strip_track_number(file.name)
            target_path = target_dir / clean_name
            
            # Handle duplicates
            if target_path.exists():
                stem = Path(clean_name).stem
                suffix = file.suffix
                counter = 1
                while target_path.exists():
                    target_path = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            try:
                shutil.move(str(file), str(target_path))
                already_moved.add(str(file))
                if file.suffix in audio_extensions:  # Only count audio files
                    newly_moved.append(clean_name)
            except Exception:
                pass  # File might still be writing
    
    return newly_moved

def flatten_downloads(temp_dir: Path, final_dir: Path, playlist_name: str = None, include_lrc: bool = True):
    """
    Flatten gamdl's Artist/Album structure to a flat structure.
    Strips track number prefixes from filenames.
    
    Args:
        include_lrc: If True, move .lrc files too. If False, only audio files.
    """
    import shutil
    
    # File types to move
    audio_extensions = ['.m4a', '.flac', '.mp3', '.opus', '.aac']
    if include_lrc:
        all_extensions = audio_extensions + ['.lrc']
    else:
        all_extensions = audio_extensions
    
    all_files = []
    for ext in all_extensions:
        all_files.extend(temp_dir.rglob(f'*{ext}'))
    
    if playlist_name:
        target_dir = final_dir / playlist_name
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = final_dir
        target_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    for file in all_files:
        # Strip track number prefix
        clean_name = strip_track_number(file.name)
        target_path = target_dir / clean_name
        
        if target_path.exists():
            stem = Path(clean_name).stem
            suffix = file.suffix
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
        shutil.move(str(file), str(target_path))
        # Only count audio files for the total
        if file.suffix in audio_extensions:
            moved_count += 1
    
    # Clean up empty temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return moved_count

def extract_playlist_name(url: str) -> str:
    """Extract playlist name from URL for folder naming."""
    # For library playlists like pl.u-XXX, we'll get the name from gamdl output
    # For now, extract the slug from URL or return None
    import re
    match = re.search(r'/playlist/([^/]+)/', url)
    if match:
        return match.group(1).replace('-', ' ').title()
    return None

def run_download(url: str, options: dict, downloads_dir: Path, cookies_path: Path) -> bool:
    """
    Run the download process for a single URL.
    - Downloads to temp folder
    - Moves files incrementally as each track completes
    - Verifies all tracks downloaded at the end
    """
    import shutil
    import re
    import time
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    
    # Create temp directory for gamdl output
    temp_dir = downloads_dir / ".gamdl_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if this is a playlist URL and extract name
    is_playlist = 'playlist' in url.lower()
    playlist_name = extract_playlist_name(url) if is_playlist else None
    
    # Construct gamdl command
    cmd = [
        sys.executable, "-m", "gamdl",
        "--cookies-path", str(cookies_path),
        "--output-path", str(temp_dir),
        url
    ]

    # Add codec arguments
    audio_format = options['format']
    if audio_format in ['aac-legacy', 'aac-he-legacy', 'alac', 'opus', 'flac']:
        cmd.extend(["--song-codec", audio_format])
    elif audio_format == 'mp3':
        cmd.extend(["--song-codec", "mp3"])
    
    # Handle lyrics option
    # gamdl by default: downloads audio + embeds lyrics + saves .lrc files
    lyrics_option = options.get('lyrics_option', 'embedded')
    if lyrics_option == 'none':
        # No lyrics at all - skip synced lyrics
        cmd.extend(["--no-synced-lyrics"])
    # 'lrc' and 'embedded' both use default behavior (audio + lyrics)
    # The difference is handled in post-processing:
    # - 'lrc': keep .lrc files, gamdl embeds lyrics by default anyway
    # - 'embedded': keep .lrc files too (user may want both)

    print_info(f"Downloading [{options['desc']}]...")
    
    # Execute and stream output
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Tracking
    total_tracks = 0
    current_track = 0
    detected_playlist_name = None
    downloaded_songs = []
    failed_songs = []
    already_moved = set()
    
    progress_pattern = re.compile(r'\[Track (\d+)/(\d+)\]')
    song_pattern = re.compile(r'Downloading "([^"]+)"')
    
    # Determine target directory
    target_dir = downloads_dir  # Will be updated when playlist name is detected
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30, complete_style="green", finished_style="green"),
        TextColumn("[bold]{task.completed}/{task.total}"),
        console=console,
        transient=False
    ) as progress:
        
        task_id = progress.add_task("Starting...", total=1, completed=0)
        last_move_check = time.time()
        current_song_name = None
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                line = line.strip()
                
                # Extract playlist name
                if 'Processing' in line:
                    name_match = re.search(r'playlist/([^/]+)/', line)
                    if name_match and not detected_playlist_name:
                        raw_name = name_match.group(1)
                        detected_playlist_name = raw_name.replace('-', ' ').replace('%20', ' ')
                        # Update target directory
                        target_dir = downloads_dir / detected_playlist_name
                        target_dir.mkdir(parents=True, exist_ok=True)
                
                # Parse track progress [Track 1/99]
                match = progress_pattern.search(line)
                if match:
                    current_track = int(match.group(1))
                    total_tracks = int(match.group(2))
                    progress.update(task_id, total=total_tracks, completed=current_track, 
                                   description="Downloading")
                # Track song being downloaded
                song_match = song_pattern.search(line)
                if song_match:
                    current_song_name = song_match.group(1)
                    # Truncate long names for display
                    display_name = current_song_name[:37] + "..." if len(current_song_name) > 40 else current_song_name
                    console.print(f"[green]➜[/green] {display_name}")
                    downloaded_songs.append(current_song_name)
                
                # Track any download failures (simple tracking)
                if "Error downloading" in line or "Skipping" in line:
                    if current_song_name and current_song_name not in failed_songs:
                        failed_songs.append(current_song_name)
                        console.print(f"[red]✗[/red] {current_song_name[:40]} - Failed")
                
                # Incremental move: check for new files every few seconds
                if time.time() - last_move_check > 2:
                    if detected_playlist_name:
                        include_lrc = (lyrics_option == 'lrc')
                        move_new_files(temp_dir, target_dir, already_moved, include_lrc)
                    last_move_check = time.time()
        
        # Mark complete
        if total_tracks > 0:
            progress.update(task_id, completed=total_tracks)

    # Final move of any remaining files
    final_playlist_name = detected_playlist_name or playlist_name
    if final_playlist_name:
        target_dir = downloads_dir / final_playlist_name
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = downloads_dir
    
    # Move any remaining files - only include .lrc if user chose 'lrc' option
    include_lrc = (lyrics_option == 'lrc')
    remaining = flatten_downloads(temp_dir, downloads_dir, final_playlist_name, include_lrc)
    
    # Count total files in target
    audio_extensions = ['.m4a', '.flac', '.mp3', '.opus', '.aac']
    final_files = []
    for ext in audio_extensions:
        final_files.extend(target_dir.rglob(f'*{ext}'))
    
    files_downloaded = len(final_files)
    
    # Verification Report
    print()
    if final_playlist_name:
        print_success(f"📁 {files_downloaded} file(s) → Downloads/{final_playlist_name}/")
    else:
        print_success(f"📁 {files_downloaded} file(s) → Downloads/")
    
    # Check for discrepancies and show failed songs
    if failed_songs:
        print_warning(f"⚠ {len(failed_songs)} track(s) failed:")
        for song in failed_songs[:10]:  # Show first 10
            console.print(f"  [red]•[/red] {song[:50]} - Failed")
        if len(failed_songs) > 10:
            console.print(f"  [dim]... and {len(failed_songs) - 10} more[/dim]")
    elif total_tracks > 0 and files_downloaded >= total_tracks:
        print_success(f"✓ All {total_tracks} tracks downloaded successfully!")
    
    return process.returncode == 0 and files_downloaded > 0

def main():
    try:
        print_banner()
        
        if not check_dependencies():
            sys.exit(1)
            
        # 1. Select Format
        format_options = select_format()
        if not format_options:
            print_info("Goodbye! 👋")
            sys.exit(0)
        
        # 2. Select lyrics option
        from tui import select_lyrics_option
        lyrics_option = select_lyrics_option()
        format_options['lyrics_option'] = lyrics_option
            
        # 3. Select Cookies
        cookies_path = select_cookies_file()
        if not cookies_path:
            print_warning("No cookies selected. Exiting.")
            sys.exit(1)
        print_success(f"Using cookies: {cookies_path.name}")
        
        # 4. Main Loop
        downloads_dir = Path.cwd() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)
        
        while True:
            url = get_url()
            if not url:
                break
                
            run_download(url, format_options, downloads_dir, cookies_path)
            
            # Explicit "Download more?" prompt per request
            from tui import ask_download_more
            if not ask_download_more():
                break
            
        # 4. Optional Cleanup
        destroy_cookies_option(cookies_path)
        print_info("Goodbye! 👋")
        
    except KeyboardInterrupt:
        print("\n")
        print_info("Exiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        # In a real scenario, we might log this to a file
        sys.exit(1)

if __name__ == "__main__":
    main()
