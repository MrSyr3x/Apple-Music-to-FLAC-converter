"""
Interactive TUI for Music Downloader
Beautiful menu-driven interface using rich and InquirerPy
"""

import sys
import shutil
from pathlib import Path
from typing import Optional, List

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

# Initialize console
console = Console() if RICH_AVAILABLE else None


def print_banner():
    """Print the application banner."""
    if RICH_AVAILABLE:
        banner = """
[bold magenta]╔══════════════════════════════════════════╗[/]
[bold magenta]║[/]  [bold cyan]🎵 Music Downloader[/] [dim]v2.0[/]               [bold magenta]║[/]
[bold magenta]║[/]  [dim]Apple Music • Spotify • YouTube[/]        [bold magenta]║[/]
[bold magenta]╚══════════════════════════════════════════╝[/]
"""
        console.print(banner)
    else:
        print("\n🎵 Music Downloader v2.0")
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
        {"name": "▶️  YouTube Music (no login needed)", "value": "youtube"},
        {"name": "🎧 Spotify (via YouTube search)", "value": "spotify"},
        Separator(),
        {"name": "❌ Exit", "value": None}
    ]
    
    return inquirer.select(
        message="Select platform:",
        choices=choices,
        default="apple"
    ).execute()


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
        
        lyrics = input("Include lyrics? (y/n): ").lower().strip() == 'y'
        flat = input("Flat structure (no artist folders)? (y/n): ").lower().strip() == 'y'
        return {"format": audio_format, "lyrics": lyrics, "flat": flat}
    
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
    
    flat = inquirer.confirm(
        message="Flat structure (no artist folders)?",
        default=True
    ).execute()
    
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


def run_download(platform: str, url: str, options: dict, cookies_path: Optional[Path] = None) -> bool:
    """Execute the download based on platform."""
    downloads_dir = get_downloads_dir()
    audio_format = options.get("format", "flac")
    
    print_info(f"Downloading to: {downloads_dir}")
    print_info(f"Format: {audio_format.upper()}")
    
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Downloading...", total=None)
            
            if platform == "apple":
                success = apple.download_apple_music(
                    url=url,
                    cookies_path=cookies_path,
                    output_dir=downloads_dir,
                    include_lyrics=options.get("lyrics", False),
                    flat_structure=options.get("flat", True)
                )
            elif platform == "spotify":
                success = spotify.download_spotify(
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
    else:
        print("Downloading...")
        if platform == "apple":
            success = apple.download_apple_music(
                url=url,
                cookies_path=cookies_path,
                output_dir=downloads_dir,
                include_lyrics=options.get("lyrics", False),
                flat_structure=options.get("flat", True)
            )
        elif platform == "spotify":
            success = spotify.download_spotify(
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
    
    # Post-processing
    if success and options.get("flat", True):
        moved = flatten_downloads(downloads_dir)
        if moved > 0:
            print_info(f"Organized {moved} files")
    
    if success and not options.get("lyrics", False):
        deleted = delete_lyrics_files(downloads_dir)
        if deleted > 0:
            print_info(f"Removed {deleted} lyrics files")
    
    return success


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
    
    # Get options
    options = get_download_options(platform)
    
    # Show summary
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            f"[bold]Platform:[/] {platform.title()}\n"
            f"[bold]URL:[/] {url[:50]}...\n"
            f"[bold]Format:[/] {options['format'].upper()}\n"
            f"[bold]Lyrics:[/] {'Yes' if options['lyrics'] else 'No'}\n"
            f"[bold]Flat structure:[/] {'Yes' if options['flat'] else 'No'}",
            title="📥 Download Summary",
            border_style="green"
        ))
        console.print()
    
    # Run download
    success = run_download(platform, url, options, cookies_path)
    
    if success:
        print_success("Download complete! 🎉")
        
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
                f"📁 {get_downloads_dir()}",
                border_style="green"
            ))
    else:
        print_error("Download failed")
        print_info("Check your URL and try again")


if __name__ == "__main__":
    run_tui()
