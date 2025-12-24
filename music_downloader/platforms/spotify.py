"""
Spotify platform handler
Uses spotdl with rich progress display
"""

import asyncio
import subprocess
import sys
import re
import time
from pathlib import Path
from typing import Tuple, List

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None


def _ensure_event_loop():
    """Fix for Python 3.14+."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def _get_url_type(url: str) -> str:
    """Detect the type of Spotify URL."""
    if "/track/" in url:
        return "track"
    elif "/album/" in url:
        return "album"
    elif "/playlist/" in url:
        return "playlist"
    return "unknown"


def _download_with_progress(cmd: list) -> Tuple[int, List[str], int, List[str]]:
    """
    Run spotdl with rich progress display.
    Returns (completed_count, failed_songs, total_found, downloaded_songs)
    """
    failed_songs = []
    downloaded_songs = []
    completed = 0
    total_found = 0
    current_song = ""
    start_time = time.time()
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**dict(__import__('os').environ), 'PYTHONUNBUFFERED': '1'}
    )
    
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console,
            transient=False
        ) as progress:
            
            finding_task = progress.add_task("[cyan]Finding songs...", total=None)
            download_task = None
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line:
                    continue
                
                # Found song
                if "Found" in line and "URL" in line:
                    total_found += 1
                    progress.update(finding_task, description=f"[cyan]Finding songs... {total_found} found")
                
                # Downloading a song - extract name
                elif "Downloading" in line:
                    match = re.search(r'"(.+?)"', line)
                    if match:
                        current_song = match.group(1)
                        if download_task is None and total_found > 0:
                            progress.remove_task(finding_task)
                            download_task = progress.add_task(
                                f"[yellow]⬇ {current_song[:40]}...",
                                total=total_found
                            )
                        elif download_task:
                            progress.update(download_task, description=f"[yellow]⬇ {current_song[:40]}...")
                
                # Download completed
                elif "Done" in line or "Downloaded" in line:
                    completed += 1
                    if current_song:
                        downloaded_songs.append(current_song)
                    if download_task:
                        progress.update(download_task, completed=completed, description=f"[green]✓ {current_song[:40]}")
                
                # Skipped (already exists)
                elif "Skipping" in line:
                    completed += 1
                    match = re.search(r'"(.+?)"', line)
                    if match:
                        downloaded_songs.append(match.group(1))
                    if download_task:
                        progress.update(download_task, completed=completed, description=f"[dim]⏭ Already exists")
                
                # Error
                elif "Error" in line or "Unable" in line:
                    match = re.search(r'"(.+?)"', line)
                    if match:
                        song_name = match.group(1)
                        failed_songs.append(song_name)
                        # Print failed song name immediately
                        console.print(f"\n  [red]✗ Failed: {song_name}[/red]")
                        if download_task:
                            progress.update(download_task, description=f"[red]✗ {song_name[:40]}")
    else:
        # Fallback without Rich
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
            
            if "Found" in line and "URL" in line:
                total_found += 1
                if total_found % 50 == 0:
                    print(f"  🔍 Finding songs... {total_found} found", flush=True)
            
            elif "Done" in line or "Downloaded" in line:
                completed += 1
                print(f"  ✓ Downloaded: {completed}/{total_found}", flush=True)
            
            elif "Error" in line or "Unable" in line:
                match = re.search(r'"(.+?)"', line)
                if match:
                    song_name = match.group(1)
                    failed_songs.append(song_name)
                    print(f"\n  ✗ Failed: {song_name}", flush=True)
    
    process.wait()
    
    # Show summary with speed
    elapsed = time.time() - start_time
    if completed > 0 and elapsed > 0:
        speed = completed / elapsed * 60  # songs per minute
        if RICH_AVAILABLE:
            console.print(f"\n  [dim]Speed: {speed:.1f} songs/min • Time: {elapsed:.0f}s[/dim]")
        else:
            print(f"\n  Speed: {speed:.1f} songs/min • Time: {elapsed:.0f}s")
    
    return completed, failed_songs, total_found, downloaded_songs


def download_spotify(
    url: str,
    output_dir: Path,
    audio_format: str = "mp3",
    include_lyrics: bool = False
) -> Tuple[bool, List[str]]:
    """Download from Spotify with rich progress display."""
    _ensure_event_loop()
    
    url_type = _get_url_type(url)
    
    if url_type == "track":
        template = "{title}.{ext}"
    elif url_type == "playlist":
        template = "{playlist}/{title}.{ext}"
    elif url_type == "album":
        template = "{album}/{title}.{ext}"
    else:
        template = "{artist}/{title}.{ext}"
    
    format_map = {"flac": "flac", "mp3": "mp3", "m4a": "m4a", "opus": "opus", "ogg": "ogg"}
    spotdl_format = format_map.get(audio_format, "mp3")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent.parent / "spotdl_wrapper.py"),
        url,
        "--output", str(output_dir),
        "-p", template,
        "--output-format", spotdl_format,
        "--download-threads", "4",
        "--search-threads", "4",
    ]
    
    if RICH_AVAILABLE:
        console.print("\n  [bold]📥 Downloading from Spotify...[/bold]")
        console.print("  [dim](Large playlists may take a while)[/dim]\n")
    else:
        print("\n  📥 Downloading from Spotify...")
        print("  (Large playlists may take a while)\n")
    
    try:
        # First attempt
        completed, failed_songs, total_found, downloaded = _download_with_progress(cmd)
        
        # Auto-retry failed songs (up to 2 more attempts)
        retry_count = 0
        while failed_songs and retry_count < 2:
            retry_count += 1
            
            if RICH_AVAILABLE:
                console.print(f"\n  [yellow]🔄 Retrying {len(failed_songs)} failed songs (attempt {retry_count + 1}/3)...[/yellow]")
            else:
                print(f"\n  🔄 Retrying {len(failed_songs)} failed songs (attempt {retry_count + 1}/3)...")
            
            time.sleep(3)
            
            new_completed, still_failed, _, new_downloaded = _download_with_progress(cmd)
            completed += new_completed
            downloaded.extend(new_downloaded)
            
            if len(still_failed) < len(failed_songs):
                recovered = len(failed_songs) - len(still_failed)
                if RICH_AVAILABLE:
                    console.print(f"  [green]✓ Recovered {recovered} songs on retry[/green]")
                else:
                    print(f"  ✓ Recovered {recovered} songs on retry")
            
            failed_songs = still_failed
            
            if not failed_songs:
                break
        
        # Count actual downloaded files instead of using counter (which double-counts on retry)
        audio_extensions = {'.mp3', '.m4a', '.flac', '.opus', '.ogg', '.wav'}
        actual_downloaded = sum(1 for f in output_dir.rglob('*') if f.suffix.lower() in audio_extensions)
        
        # Summary
        print()
        if RICH_AVAILABLE:
            if len(failed_songs) == 0:
                console.print(f"  [bold green]📊 Downloaded: {actual_downloaded} songs[/bold green]")
            else:
                console.print(f"  [bold]📊 Downloaded: {actual_downloaded}, [red]Failed: {len(failed_songs)}[/red][/bold]")
        else:
            print(f"  📊 Downloaded: {actual_downloaded}, Failed: {len(failed_songs)}")
        
        # Show failed songs
        if failed_songs:
            print()
            if RICH_AVAILABLE:
                console.print("  [red]❌ Failed songs:[/red]")
                for song in failed_songs:
                    console.print(f"     [dim]•[/dim] {song}")
            else:
                print("  ❌ Failed songs:")
                for song in failed_songs:
                    print(f"     • {song}")
        
        print()
        
        return (True, failed_songs)
        
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n  [yellow]⚠ Download cancelled by user[/yellow]\n")
        else:
            print("\n  ⚠ Download cancelled by user\n")
        return (False, [])
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n  [red]❌ Error: {e}[/red]\n")
        else:
            print(f"\n  ❌ Error: {e}\n")
        return (False, [])


def validate_spotify_url(url: str) -> bool:
    """Check if URL is a valid Spotify URL."""
    pattern = r'https?://(open\.)?spotify\.com/(track|album|playlist|artist)/.+'
    return bool(re.match(pattern, url))


def get_playlist_tracks(url: str) -> List[str]:
    """
    Get all track names from a Spotify playlist/album using spotipy.
    Returns list of track names in format "Artist - Title".
    """
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
    except ImportError:
        return []
    
    # Extract playlist/album ID from URL
    url_type = _get_url_type(url)
    
    if url_type == "track":
        return []  # Single track, no need to compare
    
    # Extract ID from URL
    if url_type == "playlist":
        match = re.search(r'/playlist/([a-zA-Z0-9]+)', url)
    elif url_type == "album":
        match = re.search(r'/album/([a-zA-Z0-9]+)', url)
    else:
        return []
    
    if not match:
        return []
    
    item_id = match.group(1)
    
    try:
        # Use spotdl's embedded credentials (they work for public data)
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='5f573c9620494bae87890c0f08a60293',
            client_secret='212476d9b0f3472eaa762d90b19b0ba8'
        ))
        
        tracks = []
        
        if url_type == "playlist":
            results = sp.playlist_tracks(item_id)
            while results:
                for item in results['items']:
                    if item['track']:
                        track = item['track']
                        artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                        title = track['name']
                        tracks.append(f"{artist} - {title}")
                
                # Handle pagination
                if results['next']:
                    results = sp.next(results)
                else:
                    break
        
        elif url_type == "album":
            results = sp.album_tracks(item_id)
            album_info = sp.album(item_id)
            album_artist = album_info['artists'][0]['name'] if album_info['artists'] else 'Unknown'
            
            while results:
                for track in results['items']:
                    artist = track['artists'][0]['name'] if track['artists'] else album_artist
                    title = track['name']
                    tracks.append(f"{artist} - {title}")
                
                if results['next']:
                    results = sp.next(results)
                else:
                    break
        
        return tracks
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"  [dim]Could not get playlist info: {e}[/dim]")
        return []


def _normalize_title(title: str) -> str:
    """Normalize a song title for comparison."""
    # Lowercase
    title = title.lower()
    # Remove common patterns
    title = re.sub(r'\s*\(.*?\)\s*', ' ', title)  # Remove (anything in parens)
    title = re.sub(r'\s*\[.*?\]\s*', ' ', title)  # Remove [anything in brackets]
    title = re.sub(r'\s*-\s*remix.*', '', title)  # Remove "- remix..."
    title = re.sub(r'\s*feat\.?\s*.*', '', title)  # Remove "feat..."
    title = re.sub(r'\s*ft\.?\s*.*', '', title)   # Remove "ft..."
    # Remove special characters
    title = re.sub(r'[^\w\s]', '', title)
    # Normalize whitespace
    title = ' '.join(title.split())
    return title.strip()


def find_missing_songs(url: str, output_dir: Path) -> List[str]:
    """
    Compare playlist tracks with downloaded files to find missing songs.
    Uses fuzzy matching to reduce false positives.
    Returns list of missing track names.
    """
    # Get all tracks from playlist
    all_tracks = get_playlist_tracks(url)
    
    if not all_tracks:
        return []
    
    # Get downloaded files and normalize them
    audio_extensions = {'.mp3', '.m4a', '.flac', '.opus', '.ogg', '.wav'}
    downloaded_normalized = []
    
    for f in output_dir.rglob('*'):
        if f.suffix.lower() in audio_extensions:
            normalized = _normalize_title(f.stem)
            downloaded_normalized.append(normalized)
    
    # Find missing
    missing = []
    for track in all_tracks:
        # Extract title part (after " - ")
        if ' - ' in track:
            title = track.split(' - ', 1)[1]
        else:
            title = track
        
        title_normalized = _normalize_title(title)
        
        # Check if any downloaded file matches (partial match)
        found = False
        for downloaded in downloaded_normalized:
            # Check if significant words match
            title_words = set(title_normalized.split())
            downloaded_words = set(downloaded.split())
            
            # If most words match (>50%), consider it found
            if title_words and downloaded_words:
                common = title_words & downloaded_words
                match_ratio = len(common) / min(len(title_words), len(downloaded_words))
                if match_ratio >= 0.5:
                    found = True
                    break
            
            # Also check direct substring match
            if title_normalized in downloaded or downloaded in title_normalized:
                found = True
                break
        
        if not found:
            missing.append(track)
    
    return missing


def find_duplicates(url: str) -> List[tuple]:
    """
    Find duplicate tracks in a Spotify playlist.
    Returns list of (track_name, count) for duplicates.
    """
    from collections import Counter
    
    tracks = get_playlist_tracks(url)
    if not tracks:
        return []
    
    counter = Counter(tracks)
    duplicates = [(track, count) for track, count in counter.items() if count > 1]
    return duplicates


def analyze_playlist(url: str, output_dir: Path, failed_songs: List[str] = None) -> dict:
    """
    Comprehensive playlist analysis after download.
    Shows: duplicates, missing songs, failed songs, summary.
    Saves missing songs to file for large playlists.
    
    Returns dict with analysis results.
    """
    if _get_url_type(url) not in ['playlist', 'album']:
        return {}
    
    if RICH_AVAILABLE:
        console.print("\n  [bold]📊 Playlist Analysis[/bold]")
        console.print("  " + "─" * 40)
    else:
        print("\n  📊 Playlist Analysis")
        print("  " + "─" * 40)
    
    results = {
        'total_in_playlist': 0,
        'duplicates': [],
        'missing': [],
        'failed': failed_songs or [],
        'downloaded': 0
    }
    
    # Get all tracks from playlist
    all_tracks = get_playlist_tracks(url)
    results['total_in_playlist'] = len(all_tracks)
    
    if not all_tracks:
        if RICH_AVAILABLE:
            console.print("  [dim]Could not analyze playlist (rate limited or error)[/dim]")
        else:
            print("  Could not analyze playlist (rate limited or error)")
        return results
    
    # 1. Count downloaded files
    audio_extensions = {'.mp3', '.m4a', '.flac', '.opus', '.ogg', '.wav'}
    downloaded_files = []
    for f in output_dir.rglob('*'):
        if f.suffix.lower() in audio_extensions:
            downloaded_files.append(f.stem.lower())
    
    downloaded_count = len(downloaded_files)
    results['downloaded'] = downloaded_count
    
    # 2. Check for duplicates
    duplicates = find_duplicates(url)
    results['duplicates'] = duplicates
    duplicate_extras = sum(count - 1 for _, count in duplicates)
    unique_tracks = len(all_tracks) - duplicate_extras
    
    if duplicates:
        if RICH_AVAILABLE:
            console.print(f"\n  [yellow]🔁 {len(duplicates)} duplicate songs in playlist:[/yellow]")
            for track, count in duplicates[:5]:
                console.print(f"     [dim]{count}x[/dim] {track}")
            if len(duplicates) > 5:
                console.print(f"     [dim]... and {len(duplicates) - 5} more[/dim]")
        else:
            print(f"\n  🔁 {len(duplicates)} duplicate songs in playlist:")
            for track, count in duplicates[:5]:
                print(f"     {count}x {track}")
            if len(duplicates) > 5:
                print(f"     ... and {len(duplicates) - 5} more")
    
    # 3. Find missing songs - use STRICT matching
    missing = []
    for track in all_tracks:
        # Extract title part (after " - ")
        if ' - ' in track:
            title = track.split(' - ', 1)[1]
        else:
            title = track
        
        # Normalize for comparison
        title_clean = re.sub(r'[^\w\s]', '', title.lower())
        title_clean = ' '.join(title_clean.split())
        
        # Check if ANY downloaded file contains this title (or vice versa)
        found = False
        for downloaded in downloaded_files:
            downloaded_clean = re.sub(r'[^\w\s]', '', downloaded)
            downloaded_clean = ' '.join(downloaded_clean.split())
            
            # Check substring match (stricter)
            if title_clean in downloaded_clean or downloaded_clean in title_clean:
                found = True
                break
            
            # Check first 3 words match
            title_words = title_clean.split()[:3]
            downloaded_words = downloaded_clean.split()[:3]
            if title_words and downloaded_words:
                if title_words == downloaded_words:
                    found = True
                    break
        
        if not found:
            missing.append(track)
    
    # Remove duplicates from missing (keep unique)
    seen = set()
    unique_missing = []
    for song in missing:
        if song not in seen:
            seen.add(song)
            unique_missing.append(song)
    missing = unique_missing
    results['missing'] = missing
    
    # 4. Check if download count doesn't match (backup detection)
    count_mismatch = downloaded_count < unique_tracks
    
    # 5. Show missing songs
    if missing or count_mismatch:
        actual_missing = max(len(missing), unique_tracks - downloaded_count)
        
        if RICH_AVAILABLE:
            console.print(f"\n  [red]❌ {actual_missing} songs not downloaded:[/red]")
            if missing:
                for song in missing[:10]:
                    console.print(f"     [dim]•[/dim] {song}")
                if len(missing) > 10:
                    console.print(f"     [dim]... and {len(missing) - 10} more[/dim]")
            else:
                console.print(f"     [dim](Could not identify specific songs)[/dim]")
        else:
            print(f"\n  ❌ {actual_missing} songs not downloaded:")
            if missing:
                for song in missing[:10]:
                    print(f"     • {song}")
                if len(missing) > 10:
                    print(f"     ... and {len(missing) - 10} more")
            else:
                print(f"     (Could not identify specific songs)")
        
        # Save missing songs to file for large playlists
        if missing:
            missing_file = output_dir / "MISSING_SONGS.txt"
            try:
                with open(missing_file, 'w') as f:
                    f.write(f"Missing songs from playlist ({len(missing)} total):\n")
                    f.write("=" * 50 + "\n\n")
                    for song in missing:
                        f.write(f"• {song}\n")
                if RICH_AVAILABLE:
                    console.print(f"\n  [yellow]📄 Full list saved to: MISSING_SONGS.txt[/yellow]")
                else:
                    print(f"\n  📄 Full list saved to: MISSING_SONGS.txt")
            except:
                pass
    
    # 6. Show failed songs (if any)
    if failed_songs:
        if RICH_AVAILABLE:
            console.print(f"\n  [red]⚠ {len(failed_songs)} songs failed during download:[/red]")
            for song in failed_songs[:5]:
                console.print(f"     [dim]•[/dim] {song}")
        else:
            print(f"\n  ⚠ {len(failed_songs)} songs failed during download:")
            for song in failed_songs[:5]:
                print(f"     • {song}")
    
    # 7. Summary
    if RICH_AVAILABLE:
        console.print(f"\n  [bold]Summary:[/bold]")
        console.print(f"     Playlist tracks: {len(all_tracks)}" + (f" ({len(duplicates)} duplicates)" if duplicates else ""))
        console.print(f"     Unique tracks:   {unique_tracks}")
        console.print(f"     Downloaded:      {downloaded_count}")
        if downloaded_count >= unique_tracks and not missing and not failed_songs:
            console.print(f"     [green]✓ All songs downloaded successfully![/green]")
        elif downloaded_count < unique_tracks:
            diff = unique_tracks - downloaded_count
            console.print(f"     [red]✗ Missing: {diff} songs[/red]")
    else:
        print(f"\n  Summary:")
        print(f"     Playlist tracks: {len(all_tracks)}" + (f" ({len(duplicates)} duplicates)" if duplicates else ""))
        print(f"     Unique tracks:   {unique_tracks}")
        print(f"     Downloaded:      {downloaded_count}")
        if downloaded_count >= unique_tracks and not missing and not failed_songs:
            print(f"     ✓ All songs downloaded successfully!")
        elif downloaded_count < unique_tracks:
            diff = unique_tracks - downloaded_count
            print(f"     ✗ Missing: {diff} songs")
    
    print()
    return results


def get_required_dependencies() -> list:
    return ["spotdl", "ffmpeg"]


