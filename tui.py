import os
import sys
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import PathValidator

# Initialize Rich Console
console = Console()

def print_banner():
    """Print the application banner."""
    console.clear()
    banner_text = Text(justify="center")
    banner_text.append("\nEnable Apple Music Downloads\n", style="bold cyan")
    banner_text.append("v3.1 (Rebuilt)", style="dim white")
    console.print(Panel(banner_text, border_style="cyan"))

def print_success(msg: str):
    console.print(f"[green]✓ {msg}[/green]")

def print_error(msg: str):
    console.print(f"[red]✗ {msg}[/red]")

def print_info(msg: str):
    console.print(f"[blue]ℹ {msg}[/blue]")

def print_warning(msg: str):
    console.print(f"[yellow]⚠ {msg}[/yellow]")

def select_format() -> Optional[dict]:
    """
    Interactive prompt to select audio format.
    Returns a dict with 'format', 'extension', and 'desc' or None if exited.
    """
    print()
    choices = [
        Choice(value="aac", name="🎵 AAC 256 (~7 MB/song) - Standard"),
        Choice(value="alac", name="🎶 ALAC (~30 MB/song) - Lossless"),
        Choice(value="flac", name="💿 FLAC (~35 MB/song) - Converted Lossless"),
        Choice(value="mp3", name="🎧 MP3 320 (~8 MB/song) - Universal"),
        Choice(value="opus", name="🔈 Opus (~6 MB/song) - Efficient"),
        Separator(),
        Choice(value=None, name="🔙 Exit")
    ]

    selected_format = inquirer.select(
        message="Select Audio Format:",
        choices=choices,
        default="aac",
        pointer=">"
    ).execute()

    if selected_format is None:
        return None

    # Return details for the selected format
    start_format_map = {
        "aac": {"format": "aac-legacy", "extension": "m4a", "desc": "AAC 256kbps"},
        "alac": {"format": "alac", "extension": "m4a", "desc": "Apple Lossless"},
        "flac": {"format": "flac", "extension": "flac", "desc": "FLAC (Converted)"},
        "mp3": {"format": "mp3", "extension": "mp3", "desc": "MP3 320kbps"},
        "opus": {"format": "opus", "extension": "opus", "desc": "Opus Codec"},
    }
    return start_format_map.get(selected_format)

def find_cookie_files() -> List[Path]:
    """Find potential cookie files in the current directory."""
    cwd = Path.cwd()
    return list(cwd.glob("*.txt"))

def select_cookies_file() -> Optional[Path]:
    """
    Interactive prompt to select a cookies file.
    """
    print()
    # Find likely cookie files to set as default
    found_cookies = find_cookie_files()
    default_path = str(found_cookies[0]) if found_cookies else str(Path.home() / "Downloads")

    print_info("Select your cookies file (use Tab to navigate/autocomplete)")
    
    cookies_path_str = inquirer.filepath(
        message="Cookies file path:",
        default=default_path,
        validate=PathValidator(is_file=True, message="Must be a file"),
        only_directories=False,
    ).execute()

    if not cookies_path_str:
        return None

    return Path(cookies_path_str).expanduser()

def get_url() -> Optional[str]:
    """Prompt for Apple Music URL."""
    print()
    url = inquirer.text(
        message="Enter Apple Music URL (or 'q' to finish):",
        validate=lambda x: True, # Basic validation handled in loop
    ).execute()
    
    if not url or url.lower() in ('q', 'quit', 'exit'):
        return None
        
    return url.strip()

def destroy_cookies_option(cookies_path: Path):
    """Option to delete the cookies file on exit."""
    if not cookies_path or not cookies_path.exists():
        return

    print()
    should_destroy = inquirer.confirm(
        message="Creating a fresh session each time is safer. Destroy cookies file?",
        default=False
    ).execute()

    if should_destroy:
        try:
            os.remove(cookies_path)
            print_success(f"Deleted: {cookies_path.name}")
        except Exception as e:
            print_error(f"Failed to delete: {e}")

def ask_download_more() -> bool:
    """Ask user if they want to download more."""
    print()
    return inquirer.confirm(
        message="Download more?",
        default=True
    ).execute()

def select_lyrics_option() -> str:
    """
    Ask user how they want lyrics handled.
    Returns: 'embedded', 'lrc', or 'none'
    """
    print()
    choices = [
        Choice(value="embedded", name="📝 Embedded (lyrics in audio file)"),
        Choice(value="lrc", name="📄 .lrc file (separate synced lyrics file)"),
        Choice(value="none", name="🚫 No lyrics"),
    ]
    
    return inquirer.select(
        message="Lyrics option:",
        choices=choices,
        default="embedded",
        pointer=">"
    ).execute()
