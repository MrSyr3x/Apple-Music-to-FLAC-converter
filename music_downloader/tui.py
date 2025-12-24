"""
🌊 Ripple - Apple Music Downloader
Public Release Version
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from InquirerPy import inquirer
    from InquirerPy.separator import Separator
    from InquirerPy.validator import PathValidator
    INQUIRER_AVAILABLE = True
except ImportError:
    INQUIRER_AVAILABLE = False

from .utils import (
    find_cookie_files, 
    get_downloads_dir, 
    get_project_dir,
    delete_file_safely,
    delete_lyrics_files,
    delete_thumbnail_files
)
from .platforms import apple
from .verify import verify_downloads_interactive
from .config import get_last_download_location, save_last_download_location, load_config

console = Console() if RICH_AVAILABLE else None


def print_banner():
    """Print the application banner."""
    print()
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║  🌊 Ripple v3.0                                ║")
    print("  ║  Apple Music Downloader (Lossless Support)     ║")
    print("  ╚════════════════════════════════════════════════╝")
    print()


# Print helpers
def print_info(msg): print(f"  ℹ {msg}")
def print_success(msg): print(f"  ✓ {msg}")
def print_error(msg): print(f"  ✗ {msg}")
def print_warning(msg): print(f"  ⚠ {msg}")


def get_url() -> Optional[str]:
    """Get Apple Music URL from user."""
    print()
    print("  Example: https://music.apple.com/album/...")
    
    try:
        if INQUIRER_AVAILABLE:
            url = inquirer.text(
                message="Paste URL:",
                mandatory=False,
            ).execute()
        else:
            url = input("  ? Paste URL: ").strip()
        
        if not url:
            return None
        return url.strip()
    except (KeyboardInterrupt, EOFError):
        return None


def select_format() -> Optional[dict]:
    """Select audio format."""
    
    if not INQUIRER_AVAILABLE:
        print("\n  Available formats:")
        print("  1. AAC 256 kbps (Standard)")
        print("  2. ALAC (Lossless)")
        print("  3. FLAC (Lossless, converted)")
        try:
            choice = input("  ? Select format [1-3]: ").strip()
            formats = {"1": "aac", "2": "alac", "3": "flac"}
            return {"format": formats.get(choice, "aac")}
        except (KeyboardInterrupt, EOFError):
            return None
    
    choices = [
        {"name": "🎵 AAC 256 (~7 MB/song) - High Quality", "value": "aac"},
        {"name": "🎶 ALAC (~30 MB/song) - Lossless", "value": "alac"},
        {"name": "💿 FLAC (~35 MB/song) - Lossless (converted)", "value": "flac"},
        Separator(),
        {"name": "🔙 Cancel", "value": None}
    ]
    
    try:
        format_choice = inquirer.select(
            message="Format:",
            choices=choices,
            default="aac"
        ).execute()
        
        if format_choice is None:
            return None
        return {"format": format_choice}
    except (KeyboardInterrupt, EOFError):
        return None


def select_download_location() -> Optional[Path]:
    """Select download location with tab completion."""
    default_dir = get_downloads_dir()
    last_location = get_last_download_location()
    
    if not INQUIRER_AVAILABLE:
        print(f"\n  Default: {default_dir}")
        try:
            custom = input("  ? Custom path (or Enter for default): ").strip()
            if custom:
                path = Path(custom).expanduser()
                path.mkdir(parents=True, exist_ok=True)
                save_last_download_location(str(path))
                return path
            return default_dir
        except (KeyboardInterrupt, EOFError):
            return None
    
    choices = [
        {"name": f"📁 Default: {default_dir}", "value": str(default_dir)},
    ]
    
    # Add last location if different from default
    if last_location and Path(last_location) != default_dir:
        choices.insert(0, {"name": f"📂 Last used: {last_location}", "value": last_location})
    
    choices.extend([
        Separator(),
        {"name": "📝 Enter custom path (with tab completion)", "value": "custom"},
        {"name": "🔙 Cancel", "value": None}
    ])
    
    try:
        location = inquirer.select(
            message="Save to:",
            choices=choices,
            default=str(default_dir)
        ).execute()
        
        if location is None:
            return None
        
        if location == "custom":
            custom_path = inquirer.filepath(
                message="Path (use Tab for autocomplete):",
                default=str(Path.home()),
                validate=PathValidator(is_dir=True, message="Must be a directory"),
                only_directories=True,
            ).execute()
            
            if custom_path:
                path = Path(custom_path).expanduser()
                path.mkdir(parents=True, exist_ok=True)
                save_last_download_location(str(path))
                return path
            return None
        
        return Path(location)
    except (KeyboardInterrupt, EOFError):
        return None


def setup_cookies() -> Optional[Path]:
    """Setup Apple Music cookies."""
    # Check for existing cookies
    cookies = find_cookie_files()
    
    if cookies:
        print_success(f"Found cookies: {cookies[0].name}")
        return cookies[0]
    
    # No cookies found - guide user
    print()
    print_warning("Apple Music requires cookies for authentication.")
    print()
    print("  To get cookies:")
    print("  1. Install a browser extension like 'Get cookies.txt LOCALLY'")
    print("  2. Go to music.apple.com and sign in")
    print("  3. Export cookies as 'cookies.txt'")
    print("  4. Place in this folder or ~/Downloads")
    print()
    
    try:
        input("  Press Enter after placing cookies.txt...")
    except (KeyboardInterrupt, EOFError):
        return None
    
    # Check again
    cookies = find_cookie_files()
    if cookies:
        print_success(f"Found: {cookies[0].name}")
        return cookies[0]
    
    print_error("No cookies found. Please try again.")
    return None


def run_download(url: str, options: dict, downloads_dir: Path, cookies_path: Path) -> bool:
    """Execute the download."""
    audio_format = options.get("format", "aac")
    
    # Create Apple Music subfolder
    downloads_dir = downloads_dir / "Apple Music"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print()
    print_info(f"Saving to: {downloads_dir}")
    print_info(f"Format: {audio_format.upper()}")
    
    # Map format to gamdl codec
    codec_map = {"aac": "aac-legacy", "alac": "alac", "flac": "alac"}
    success = apple.download_apple_music(
        url=url,
        cookies_path=cookies_path,
        output_dir=downloads_dir,
        codec=codec_map.get(audio_format, "aac-legacy"),
        include_lyrics=False
    )
    
    # Clean up
    delete_lyrics_files(downloads_dir)
    delete_thumbnail_files(downloads_dir)
    
    return success


def run_tui():
    """Main TUI entry point."""
    print_banner()
    
    # Setup cookies first
    cookies_path = setup_cookies()
    if not cookies_path:
        print_error("Cannot proceed without cookies.")
        return
    
    # Select format
    options = select_format()
    if not options:
        print("\n  ℹ Goodbye! 👋")
        return
    
    # Select download location
    downloads_dir = select_download_location()
    if not downloads_dir:
        print("\n  ℹ Goodbye! 👋")
        return
    
    # Main download loop
    while True:
        url = get_url()
        if not url:
            break
        
        if not apple.validate_apple_url(url):
            print_error("Invalid Apple Music URL")
            continue
        
        # Download
        success = run_download(url, options, downloads_dir, cookies_path)
        
        if success:
            print_success("Download complete! 🎉")
        else:
            print_error("Download failed")
        
        # Verify metadata
        verify_downloads_interactive(downloads_dir / "Apple Music")
        
        # Ask for more
        print()
        try:
            more = input("  Download more? (y/n): ").strip().lower()
            if more != 'y':
                break
        except (KeyboardInterrupt, EOFError):
            break
    
    print()
    print_info(f"Your music: {downloads_dir / 'Apple Music'}")
    print("\n  ℹ Goodbye! 👋")


if __name__ == "__main__":
    run_tui()
