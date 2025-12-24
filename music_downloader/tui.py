"""
🌊 Ripple - Music Downloader TUI
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
from .platforms import apple, spotify, youtube
from .verify import verify_downloads_interactive
from .config import get_last_download_location, save_last_download_location, load_config

console = Console() if RICH_AVAILABLE else None


def print_banner():
    """Print the application banner."""
    print()
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║  🌊 Ripple v2.2                                ║")
    print("  ║  Apple Music • Spotify • YouTube Music         ║")
    print("  ╚════════════════════════════════════════════════╝")
    print()


def print_success(msg: str):
    print(f"  ✓ {msg}")


def print_error(msg: str):
    print(f"  ✗ {msg}")


def print_info(msg: str):
    print(f"  ℹ {msg}")


def print_warning(msg: str):
    print(f"  ⚠ {msg}")


def check_dependencies():
    """Check if FFmpeg is installed."""
    if not shutil.which("ffmpeg"):
        print_error("FFmpeg is required but not installed")
        print()
        print("  Install FFmpeg:")
        print("    macOS:   brew install ffmpeg")
        print("    Windows: winget install ffmpeg")
        print("    Linux:   sudo apt install ffmpeg")
        return False
    return True


def select_platform() -> Optional[str]:
    """Show platform selection menu."""
    if not INQUIRER_AVAILABLE:
        print("\n  1. Spotify")
        print("  2. YouTube Music")
        print("  3. Apple Music (requires cookies)")
        print("  4. Exit")
        choice = input("\n  Select (1-4): ").strip()
        return {"1": "spotify", "2": "youtube", "3": "apple", "4": None}.get(choice)
    
    choices = [
        {"name": "🎧 Spotify (no login needed)", "value": "spotify"},
        {"name": "▶️  YouTube Music (no login needed)", "value": "youtube"},
        {"name": "🍎 Apple Music (requires cookies)", "value": "apple"},
        Separator(),
        {"name": "❌ Exit", "value": None}
    ]
    
    return inquirer.select(
        message="Select platform:",
        choices=choices,
        default="spotify"
    ).execute()


def select_download_location() -> Path:
    """Let user select where to save downloads with tab completion."""
    default_dir = get_downloads_dir()
    
    # Check for saved location from config
    saved_location = get_last_download_location()
    
    if not INQUIRER_AVAILABLE:
        print(f"\n  Default: {default_dir}")
        if saved_location:
            print(f"  Last used: {saved_location}")
        custom = input("  Path (Enter for default): ").strip()
        if custom:
            path = Path(custom).expanduser().resolve()
            path.mkdir(parents=True, exist_ok=True)
            save_last_download_location(path)
            return path
        return default_dir
    
    choices = [
        {"name": f"📁 Default: {default_dir}", "value": "default"},
    ]
    
    # Add saved location if different from default
    if saved_location and saved_location != default_dir:
        choices.insert(0, {"name": f"📍 Last used: {saved_location}", "value": "saved"})
    
    choices.append({"name": "📝 Enter custom path (with tab completion)", "value": "custom"})
    
    result = inquirer.select(
        message="Save to:",
        choices=choices,
        default="saved" if saved_location and saved_location != default_dir else "default"
    ).execute()
    
    if result == "default":
        save_last_download_location(default_dir)
        return default_dir
    elif result == "saved" and saved_location:
        return saved_location
    else:
        # Use filepath with tab completion
        try:
            path_str = inquirer.filepath(
                message="Path (use Tab for autocomplete):",
                default=str(Path.home()),
                only_directories=True,
            ).execute()
            
            if not path_str or not path_str.strip():
                return default_dir
            
            path = Path(path_str).expanduser().resolve()
            path.mkdir(parents=True, exist_ok=True)
            save_last_download_location(path)
            return path
        except Exception:
            # Fallback to text input
            path_str = inquirer.text(
                message="Path:",
                default=str(default_dir)
            ).execute()
            
            if not path_str or not path_str.strip():
                return default_dir
            
            path = Path(path_str).expanduser().resolve()
            try:
                path.mkdir(parents=True, exist_ok=True)
                save_last_download_location(path)
                return path
            except:
                return default_dir


def select_cookie_file() -> Optional[Path]:
    """Find and let user select a cookie file with helpful instructions."""
    found = find_cookie_files()
    
    if not found:
        print()
        print("  🍪 Cookie Setup for Apple Music")
        print("  ─────────────────────────────────────────────")
        print("  1. Use Chrome or Firefox (not Safari!)")
        print("  2. Install 'Get cookies.txt LOCALLY' extension")
        print("  3. Go to music.apple.com and log in")
        print("  4. Click extension icon → Export → Save")
        print("  5. Run Ripple again and select the file")
        print("  ─────────────────────────────────────────────")
        print()
        
        if INQUIRER_AVAILABLE:
            try:
                path_str = inquirer.filepath(
                    message="Cookie file path (use Tab):",
                    default=str(Path.home() / "Downloads"),
                ).execute()
                
                if path_str:
                    path = Path(path_str).expanduser().resolve()
                    if path.exists() and path.is_file():
                        return path
            except:
                pass
        
        path_str = input("  Cookie file path: ").strip()
        if path_str:
            path = Path(path_str).expanduser().resolve()
            if path.exists():
                return path
        return None
    
    if not INQUIRER_AVAILABLE:
        print("\n  Found cookie files:")
        for i, f in enumerate(found, 1):
            print(f"    {i}. {f.name} ({f.parent.name}/)")
        choice = input("  Select (number): ").strip()
        try:
            return found[int(choice) - 1]
        except:
            return None
    
    choices = [{"name": f"{f.name} ({f.parent.name}/)", "value": f} for f in found]
    choices.append(Separator())
    choices.append({"name": "📝 Enter path manually (with Tab)", "value": "manual"})
    
    result = inquirer.select(
        message="Cookie file:",
        choices=choices
    ).execute()
    
    if result == "manual":
        try:
            path_str = inquirer.filepath(
                message="Cookie file (use Tab):",
                default=str(Path.home() / "Downloads"),
            ).execute()
            if path_str:
                path = Path(path_str).expanduser().resolve()
                if path.exists():
                    return path
        except:
            pass
        return None
    
    return result


def get_download_options(platform: str) -> dict:
    """Get download preferences with all format options."""
    
    # Apple Music - Real lossless + all common formats
    if platform == "apple":
        formats = [
            {"name": "🍎 AAC-LC  (~4 MB/song)  - Apple Standard", "value": "aac"},
            {"name": "🍎 ALAC    (~25 MB/song) - Apple Lossless", "value": "alac"},
            {"name": "🎵 FLAC    (~25 MB/song) - Lossless", "value": "flac"},
            {"name": "🎧 MP3     (~4 MB/song)  - Universal", "value": "mp3"},
            {"name": "📱 OPUS    (~2 MB/song)  - Smallest", "value": "opus"},
            {"name": "🔊 OGG     (~3 MB/song)  - Open Format", "value": "ogg"},
        ]
    else:
        # Spotify/YouTube - No real FLAC available (sources from YouTube)
        # Being honest with users about quality limitations
        formats = [
            {"name": "🎧 MP3 320  (~4 MB/song)  - Best Available", "value": "mp3"},
            {"name": "🍎 M4A/AAC  (~4 MB/song)  - Apple Compatible", "value": "m4a"},
            {"name": "📱 OPUS     (~2 MB/song)  - Smallest", "value": "opus"},
            {"name": "🔊 OGG      (~3 MB/song)  - Open Format", "value": "ogg"},
        ]
    
    if not INQUIRER_AVAILABLE:
        print("\n  Formats:")
        for i, f in enumerate(formats, 1):
            print(f"    {i}. {f['name']}")
        choice = input(f"  Select (1-{len(formats)}): ").strip()
        try:
            audio_format = formats[int(choice) - 1]["value"]
        except:
            audio_format = "mp3"
        return {"format": audio_format}
    
    audio_format = inquirer.select(
        message="Format:",
        choices=formats,
        default="mp3" if platform != "apple" else "aac"
    ).execute()
    
    return {"format": audio_format}


def get_url(platform: str) -> Optional[str]:
    """Get URL from user."""
    examples = {
        "apple": "https://music.apple.com/...",
        "spotify": "https://open.spotify.com/...",
        "youtube": "https://music.youtube.com/..."
    }
    
    print()
    print(f"  Example: {examples.get(platform, '')}")
    
    if INQUIRER_AVAILABLE:
        url = inquirer.text(
            message="Paste URL:"
        ).execute()
    else:
        url = input("  URL: ").strip()
    
    return url if url and len(url) > 10 else None


def display_failed_songs(failed_songs: List[str], output_dir: Path):
    """Display failed songs."""
    if not failed_songs:
        return
    
    print()
    print_warning(f"{len(failed_songs)} songs failed:")
    for song in failed_songs[:5]:
        print(f"    ✗ {song[:50]}")
    if len(failed_songs) > 5:
        print(f"    ... and {len(failed_songs) - 5} more")
    
    failed_file = output_dir / "failed_songs.txt"
    with open(failed_file, 'w') as f:
        for song in failed_songs:
            f.write(f"{song}\n")
    print_info(f"Saved to: failed_songs.txt")


def ask_retry() -> bool:
    """Ask if user wants to retry via YouTube."""
    if INQUIRER_AVAILABLE:
        return inquirer.confirm(
            message="Retry failed songs via YouTube?",
            default=False
        ).execute()
    return input("  Retry via YouTube? (y/n): ").lower() == 'y'


def retry_failed_songs(failed_songs: List[str], output_dir: Path, audio_format: str):
    """Retry failed songs via YouTube search."""
    print()
    print_info(f"Retrying {len(failed_songs)} songs...")
    
    for i, song in enumerate(failed_songs, 1):
        print(f"  [{i}/{len(failed_songs)}] {song[:40]}")
        youtube.download_youtube(
            url=f"ytsearch1:{song}",
            output_dir=output_dir,
            audio_format=audio_format
        )


def run_download(platform: str, url: str, options: dict, downloads_dir: Path, cookies_path: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """Execute the download."""
    audio_format = options.get("format", "mp3")
    failed_songs = []
    
    print()
    print_info(f"Saving to: {downloads_dir}")
    print_info(f"Format: {audio_format.upper()}")
    
    if platform == "apple":
        # Map format to gamdl codec
        codec_map = {"aac": "aac-legacy", "alac": "alac", "mp3": "aac-legacy", "flac": "alac"}
        success = apple.download_apple_music(
            url=url,
            cookies_path=cookies_path,
            output_dir=downloads_dir,
            codec=codec_map.get(audio_format, "aac-legacy"),
            include_lyrics=False
        )
    elif platform == "spotify":
        success, failed_songs = spotify.download_spotify(
            url=url,
            output_dir=downloads_dir,
            audio_format=audio_format
        )
        # Check for missing songs (compare playlist to downloaded files)
        spotify.analyze_playlist(url, downloads_dir, failed_songs)
    elif platform == "youtube":
        success = youtube.download_youtube(
            url=url,
            output_dir=downloads_dir,
            audio_format=audio_format
        )
    else:
        success = False
    
    # Clean up
    delete_lyrics_files(downloads_dir)
    delete_thumbnail_files(downloads_dir)
    
    return success, failed_songs


def handle_apple_music_session(cookies_path: Path, downloads_dir: Path, options: dict):
    """Handle Apple Music session with option to download more."""
    while True:
        # Get URL
        url = get_url("apple")
        if not url:
            break
        
        if not apple.validate_apple_url(url):
            print_error("Invalid Apple Music URL")
            continue
        
        # Download
        success, _ = run_download("apple", url, options, downloads_dir, cookies_path)
        
        if success:
            print()
            print_success("Download complete! 🎉")
            verify_downloads_interactive(downloads_dir)
        
        # Ask if want to download more
        print()
        if INQUIRER_AVAILABLE:
            more = inquirer.confirm(
                message="Download more from Apple Music?",
                default=True
            ).execute()
        else:
            more = input("  Download more? (y/n): ").lower() == 'y'
        
        if not more:
            break
    
    # Now ask about cookie deletion
    print()
    print("  🔒 Cookie Security")
    print("  ─────────────────────────────────────────────")
    print("  Cookies contain your Apple Music login.")
    print("  Delete them for security, or keep for later.")
    print()
    print("  ⚠ If deleted, you'll need to export cookies")
    print("    again next time you want to download.")
    print("  ─────────────────────────────────────────────")
    print()
    
    if INQUIRER_AVAILABLE:
        delete = inquirer.confirm(
            message="Delete cookies now?",
            default=False
        ).execute()
    else:
        delete = input("  Delete cookies? (y/n): ").lower() == 'y'
    
    if delete:
        if delete_file_safely(cookies_path):
            print_success("Cookies deleted for security")
        else:
            print_warning("Could not delete cookies")
    else:
        print_info(f"Cookies kept at: {cookies_path}")


def run_tui():
    """Main entry point."""
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    # Platform
    platform = select_platform()
    if not platform:
        print_info("Goodbye! 👋")
        return
    
    # Location (for non-Apple, ask first)
    if platform != "apple":
        downloads_dir = select_download_location()
        options = get_download_options(platform)
        
        # Get URL
        url = get_url(platform)
        if not url:
            print_error("URL required")
            return
        
        # Validate
        validators = {
            "spotify": spotify.validate_spotify_url,
            "youtube": youtube.validate_youtube_url
        }
        
        if not validators[platform](url):
            print_error(f"Invalid {platform} URL")
            return
        
        # Summary
        print()
        print("  ─────────────────────────────────────────────────")
        print(f"  Platform: {platform.title()}")
        print(f"  Format:   {options['format'].upper()}")
        print(f"  Save to:  {downloads_dir}")
        print("  ─────────────────────────────────────────────────")
        
        # Download
        success, failed_songs = run_download(platform, url, options, downloads_dir)
        
        # Show failures (no retry option anymore)
        if failed_songs:
            display_failed_songs(failed_songs, downloads_dir)
        
        print()
        print_success("Download complete! 🎉")
        verify_downloads_interactive(downloads_dir)
        
    else:
        # Apple Music flow with session handling
        cookies_path = select_cookie_file()
        if not cookies_path:
            print_error("Cookies required for Apple Music")
            return
        print_success(f"Using: {cookies_path.name}")
        
        downloads_dir = select_download_location()
        options = get_download_options(platform)
        
        # Handle session with multiple downloads
        handle_apple_music_session(cookies_path, downloads_dir, options)
    
    # Final message
    print()
    print("  ═══════════════════════════════════════════════════")
    print(f"  📁 Your music: {downloads_dir}")
    print("  ═══════════════════════════════════════════════════")
    print()
    print_info("Goodbye! 👋")


if __name__ == "__main__":
    run_tui()
