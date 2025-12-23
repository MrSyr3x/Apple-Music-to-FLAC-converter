"""
Interactive TUI for Music Downloader
Beautiful menu-driven interface using rich and InquirerPy
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from InquirerPy import inquirer
    from InquirerPy.separator import Separator
    INQUIRER_AVAILABLE = True
except ImportError:
    INQUIRER_AVAILABLE = False

from .utils import (
    find_cookie_files, 
    get_downloads_dir, 
    get_project_dir,
    delete_file_safely,
    flatten_downloads,
    delete_lyrics_files
)
from .platforms import apple, spotify, youtube
from .verify import verify_downloads_interactive

# Initialize console
console = Console() if RICH_AVAILABLE else None


def print_banner():
    """Print the application banner."""
    if RICH_AVAILABLE:
        banner = """
[bold magenta]╔══════════════════════════════════════════╗[/]
[bold magenta]║[/]  [bold cyan]🎵 Music Downloader[/] [dim]v2.1[/]               [bold magenta]║[/]
[bold magenta]║[/]  [dim]Apple Music • Spotify • YouTube[/]        [bold magenta]║[/]
[bold magenta]╚══════════════════════════════════════════╝[/]
"""
        console.print(banner)
    else:
        print("\n🎵 Music Downloader v2.1")
        print("   Apple Music • Spotify • YouTube\n")


def print_success(msg: str):
    if RICH_AVAILABLE:
        console.print(f"[bold green]✓[/] {msg}")
    else:
        print(f"✓ {msg}")


def print_error(msg: str):
    if RICH_AVAILABLE:
        console.print(f"[bold red]✗[/] {msg}")
    else:
        print(f"✗ {msg}")


def print_info(msg: str):
    if RICH_AVAILABLE:
        console.print(f"[bold blue]ℹ[/] {msg}")
    else:
        print(f"ℹ {msg}")


def print_warning(msg: str):
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠[/] {msg}")
    else:
        print(f"⚠ {msg}")


def check_dependencies():
    """Check if FFmpeg is installed."""
    if not shutil.which("ffmpeg"):
        print_error("FFmpeg is required but not installed")
        print_info("Install with: brew install ffmpeg")
        return False
    return True


def select_platform() -> Optional[str]:
    """Show platform selection menu."""
    if not INQUIRER_AVAILABLE:
        print("\n1. Apple Music")
        print("2. Spotify")
        print("3. YouTube Music")
        print("4. Exit")
        choice = input("\nSelect platform (1-4): ").strip()
        return {"1": "apple", "2": "youtube", "3": "spotify", "4": None}.get(choice)
    
    choices = [
        {"name": "🍎 Apple Music (requires cookies)", "value": "apple"},
        {"name": "🎧 Spotify", "value": "spotify"},
        {"name": "▶️  YouTube Music (no login needed)", "value": "youtube"},
        Separator(),
        {"name": "❌ Exit", "value": None}
    ]
    
    return inquirer.select(
        message="Select platform:",
        choices=choices,
        default="apple"
    ).execute()


def select_download_location() -> Path:
    """Let user select where to save downloads."""
    default_dir = get_downloads_dir()
    
    if not INQUIRER_AVAILABLE:
        print(f"\nDefault download location: {default_dir}")
        custom = input("Enter custom path (or press Enter for default): ").strip()
        if custom:
            path = Path(custom).expanduser().resolve()
            path.mkdir(parents=True, exist_ok=True)
            return path
        return default_dir
    
    choices = [
        {"name": f"📁 Default ({default_dir})", "value": "default"},
        {"name": "📂 Choose custom folder...", "value": "custom"},
        {"name": "💾 Enter path manually (SD card, external drive, etc.)", "value": "manual"},
    ]
    
    result = inquirer.select(
        message="Where to save downloads?",
        choices=choices,
        default="default"
    ).execute()
    
    if result == "default":
        return default_dir
    elif result == "custom":
        try:
            path = inquirer.filepath(
                message="Select download folder:",
                only_directories=True,
                validate=lambda x: Path(x).exists()
            ).execute()
            return Path(path).resolve()
        except Exception:
            print_warning("Could not browse folders, using default")
            return default_dir
    else:  # manual
        path_str = inquirer.text(
            message="Enter full path (e.g., /Volumes/SDCard/Music):",
            validate=lambda x: len(x) > 0
        ).execute()
        
        path = Path(path_str).expanduser().resolve()
        try:
            path.mkdir(parents=True, exist_ok=True)
            # Test if writable
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
            return path
        except Exception as e:
            print_error(f"Cannot write to {path}: {e}")
            print_info("Using default location instead")
            return default_dir


def select_cookie_file() -> Optional[Path]:
    """Find and let user select a cookie file."""
    found = find_cookie_files()
    
    if not found:
        print_warning("No cookie files found")
        show_cookie_help()
        
        if INQUIRER_AVAILABLE:
            path = inquirer.filepath(
                message="Enter path to cookies file:",
                validate=lambda x: Path(x).exists()
            ).execute()
            return Path(path) if path else None
        else:
            path = input("Enter path to cookies file: ").strip()
            return Path(path) if path and Path(path).exists() else None
    
    if not INQUIRER_AVAILABLE:
        print("\nFound cookie files:")
        for i, f in enumerate(found, 1):
            print(f"  {i}. {f}")
        choice = input("Select file number: ").strip()
        try:
            return found[int(choice) - 1]
        except (ValueError, IndexError):
            return None
    
    choices = [{"name": str(f), "value": f} for f in found]
    choices.append(Separator())
    choices.append({"name": "📁 Browse for file...", "value": "browse"})
    choices.append({"name": "❓ I need help getting cookies", "value": "help"})
    
    result = inquirer.select(
        message="Select cookie file:",
        choices=choices
    ).execute()
    
    if result == "help":
        show_cookie_help()
        return select_cookie_file()
    elif result == "browse":
        path = inquirer.filepath(
            message="Enter path to cookies file:",
            validate=lambda x: Path(x).exists()
        ).execute()
        return Path(path) if path else None
    
    return result


def show_cookie_help():
    """Display cookie export instructions."""
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold]How to get cookies:[/]\n\n"
            "1. Install browser extension:\n"
            "   • Chrome: [cyan]Get cookies.txt LOCALLY[/]\n"
            "   • Firefox: [cyan]Export Cookies[/]\n\n"
            "2. Go to [bold]music.apple.com[/] and log in\n\n"
            "3. Click extension → Export cookies\n\n"
            "4. Save the file anywhere (we'll find it!)\n\n"
            "[dim]⚠ Cookie will be deleted after download for security[/]",
            title="🍪 Cookie Setup",
            border_style="cyan"
        ))
        console.print()
    else:
        print("\n📋 How to get cookies:")
        print("1. Install 'Get cookies.txt LOCALLY' extension in Chrome")
        print("2. Go to music.apple.com and log in")
        print("3. Export cookies and save anywhere")
        print()


def get_download_options(platform: str) -> dict:
    """Get download preferences from user."""
    
    # Available formats
    formats = [
        {"name": "🎵 FLAC (Lossless, largest)", "value": "flac"},
        {"name": "🎧 MP3 (Universal, good quality)", "value": "mp3"},
        {"name": "🍎 M4A/AAC (Apple format)", "value": "m4a"},
        {"name": "🎹 WAV (Uncompressed, huge)", "value": "wav"},
        {"name": "🔊 OGG (Open format)", "value": "ogg"},
        {"name": "📱 OPUS (Best compression)", "value": "opus"},
    ]
    
    if not INQUIRER_AVAILABLE:
        print("\nAvailable formats:")
        for i, f in enumerate(formats, 1):
            print(f"  {i}. {f['name']}")
        choice = input("Select format (1-6): ").strip()
        try:
            audio_format = formats[int(choice) - 1]["value"]
        except (ValueError, IndexError):
            audio_format = "flac"
        
        lyrics = platform == "apple" and input("Include lyrics? (y/n): ").lower().strip() == 'y'
        # Folder structure is now automatic based on URL type
        return {"format": audio_format, "lyrics": lyrics, "flat": True}
    
    audio_format = inquirer.select(
        message="Select audio format:",
        choices=formats,
        default="flac"
    ).execute()
    
    # Only ask about lyrics for Apple Music
    lyrics = False
    if platform == "apple":
        lyrics = inquirer.confirm(
            message="Include lyrics?",
            default=False
        ).execute()
    
    # Folder structure is now automatic:
    # - Single tracks: flat (downloads/song.ext)
    # - Playlists/Albums: named folder (downloads/PlaylistName/song.ext)
    flat = True  # Not used anymore, kept for compatibility
    
    return {"format": audio_format, "lyrics": lyrics, "flat": flat}


def get_url(platform: str) -> Optional[str]:
    """Get URL from user."""
    examples = {
        "apple": "https://music.apple.com/...",
        "spotify": "https://open.spotify.com/...",
        "youtube": "https://music.youtube.com/..."
    }
    
    if INQUIRER_AVAILABLE:
        url = inquirer.text(
            message="Paste URL:",
            validate=lambda x: len(x) > 10,
            long_instruction=f"Example: {examples.get(platform, '')}"
        ).execute()
    else:
        url = input(f"\nPaste URL ({examples.get(platform, '')}): ").strip()
    
    return url if url else None


def confirm_cookie_deletion() -> bool:
    """Ask user to confirm cookie deletion."""
    if INQUIRER_AVAILABLE:
        return inquirer.confirm(
            message="Delete cookie file for security?",
            default=True
        ).execute()
    else:
        return input("Delete cookie file for security? (y/n): ").lower().strip() == 'y'


def display_failed_songs(failed_songs: List[str], output_dir: Path):
    """Display failed songs and save to file."""
    if not failed_songs:
        return
    
    print_warning(f"{len(failed_songs)} songs failed to download")
    
    if RICH_AVAILABLE:
        console.print()
        table = Table(title="❌ Failed Songs", border_style="red")
        table.add_column("#", style="dim")
        table.add_column("Song")
        
        for i, song in enumerate(failed_songs[:20], 1):  # Show first 20
            table.add_row(str(i), song)
        
        if len(failed_songs) > 20:
            table.add_row("...", f"and {len(failed_songs) - 20} more")
        
        console.print(table)
        console.print()
    else:
        print("\nFailed songs:")
        for i, song in enumerate(failed_songs[:10], 1):
            print(f"  {i}. {song}")
        if len(failed_songs) > 10:
            print(f"  ... and {len(failed_songs) - 10} more")
    
    # Save to file
    failed_file = output_dir / "failed_songs.txt"
    with open(failed_file, 'w') as f:
        f.write(f"# Failed songs - {len(failed_songs)} total\n")
        f.write("# Search for these on Spotify/YouTube and retry individually\n\n")
        for song in failed_songs:
            f.write(f"{song}\n")
    
    print_info(f"Failed songs saved to: {failed_file}")
    return failed_file


def ask_retry_failed_songs() -> bool:
    """Ask user if they want to retry failed songs."""
    if INQUIRER_AVAILABLE:
        return inquirer.confirm(
            message="Some songs failed. Do you want to retry them via YouTube search?",
            default=True
        ).execute()
    else:
        return input("\nSome songs failed. Retry via YouTube? (y/n): ").lower().strip() == 'y'


def retry_failed_songs_via_youtube(failed_songs: List[str], output_dir: Path, audio_format: str):
    """Retry failed songs by searching YouTube."""
    print_info(f"Retrying {len(failed_songs)} songs via YouTube search...")
    
    retry_failed = []
    for i, song in enumerate(failed_songs, 1):
        print_info(f"[{i}/{len(failed_songs)}] Searching: {song}")
        
        # Use yt-dlp to search and download
        success = youtube.download_youtube(
            url=f"ytsearch1:{song}",
            output_dir=output_dir,
            audio_format=audio_format,
            flat_structure=True
        )
        
        if not success:
            retry_failed.append(song)
    
    if retry_failed:
        print_warning(f"{len(retry_failed)} songs still failed after retry")
        # Update the failed_songs.txt
        failed_file = output_dir / "failed_songs.txt"
        with open(failed_file, 'w') as f:
            f.write(f"# Failed songs after retry - {len(retry_failed)} total\n\n")
            for song in retry_failed:
                f.write(f"{song}\n")
    else:
        print_success("All retry attempts succeeded!")
        # Remove failed_songs.txt since all succeeded
        failed_file = output_dir / "failed_songs.txt"
        if failed_file.exists():
            failed_file.unlink()


def run_download(platform: str, url: str, options: dict, downloads_dir: Path, cookies_path: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """Execute the download based on platform."""
    audio_format = options.get("format", "flac")
    failed_songs = []
    
    print_info(f"Saving to: {downloads_dir}")
    print_info(f"Format: {audio_format.upper()}")
    
    # Call platform handlers - they now show their own clean progress
    if platform == "apple":
        success = apple.download_apple_music(
            url=url,
            cookies_path=cookies_path,
            output_dir=downloads_dir,
            include_lyrics=options.get("lyrics", False),
            flat_structure=options.get("flat", True)
        )
    elif platform == "spotify":
        success, failed_songs = spotify.download_spotify(
            url=url,
            output_dir=downloads_dir,
            audio_format=audio_format,
            include_lyrics=options.get("lyrics", False),
            flat_structure=options.get("flat", True)
        )
    elif platform == "youtube":
        success = youtube.download_youtube(
            url=url,
            output_dir=downloads_dir,
            audio_format=audio_format,
            flat_structure=options.get("flat", True)
        )
    else:
        success = False
    
    # Post-processing: only delete lyrics if user didn't want them
    if success and not options.get("lyrics", False):
        deleted = delete_lyrics_files(downloads_dir)
        if deleted > 0:
            print_info(f"Removed {deleted} lyrics files")
    
    return success, failed_songs


def run_tui():
    """Main TUI entry point."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Platform selection
    platform = select_platform()
    if not platform:
        print_info("Goodbye! 👋")
        return
    
    # Cookie handling for Apple Music
    cookies_path = None
    if platform == "apple":
        cookies_path = select_cookie_file()
        if not cookies_path:
            print_error("Cookie file required for Apple Music")
            return
        print_success(f"Using cookies: {cookies_path.name}")
    
    # Get URL
    url = get_url(platform)
    if not url:
        print_error("URL is required")
        return
    
    # Validate URL
    validators = {
        "apple": apple.validate_apple_url,
        "spotify": spotify.validate_spotify_url,
        "youtube": youtube.validate_youtube_url
    }
    
    if not validators[platform](url):
        print_error(f"Invalid {platform} URL")
        return
    
    # Get download location
    downloads_dir = select_download_location()
    print_success(f"Saving to: {downloads_dir}")
    
    # Get options
    options = get_download_options(platform)
    
    # Show summary
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            f"[bold]Platform:[/] {platform.title()}\n"
            f"[bold]URL:[/] {url[:50]}...\n"
            f"[bold]Save to:[/] {downloads_dir}\n"
            f"[bold]Format:[/] {options['format'].upper()}\n"
            f"[bold]Lyrics:[/] {'Yes' if options['lyrics'] else 'No'}",
            title="📥 Download Summary",
            border_style="green"
        ))
        console.print()
    
    # Run download
    success, failed_songs = run_download(platform, url, options, downloads_dir, cookies_path)
    
    # Handle failed songs
    if failed_songs:
        display_failed_songs(failed_songs, downloads_dir)
        
        # Ask if user wants to retry via YouTube
        if ask_retry_failed_songs():
            retry_failed_songs_via_youtube(
                failed_songs, 
                downloads_dir, 
                options.get("format", "flac")
            )
    
    if success:
        print_success("Download complete! 🎉")
        
        # Verify metadata
        verify_downloads_interactive(downloads_dir)
        
        # Cookie cleanup for Apple Music
        if platform == "apple" and cookies_path:
            if confirm_cookie_deletion():
                if delete_file_safely(cookies_path):
                    print_success("Cookie file deleted for security")
                else:
                    print_warning("Could not delete cookie file")
        
        if RICH_AVAILABLE:
            console.print()
            console.print(Panel.fit(
                f"[bold green]Your music is ready![/]\n\n"
                f"📁 {downloads_dir}",
                border_style="green"
            ))
    else:
        print_error("Download failed")
        print_info("Check your URL and try again")


if __name__ == "__main__":
    run_tui()
