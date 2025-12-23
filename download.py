#!/usr/bin/env python3
"""
🍎 Apple Music to FLAC

A beautiful CLI tool to download Apple Music playlists and convert to FLAC.
https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter
"""

import subprocess
import sys
import os
import argparse
import shutil
import re
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Initialize console
console = Console() if RICH_AVAILABLE else None


def print_banner():
    """Print the application banner."""
    if RICH_AVAILABLE:
        banner = """
[bold red]█████╗ [/][bold green]██████╗ ██████╗ ██╗     ███████╗[/]
[bold red]██╔══██╗[/][bold green]██╔══██╗██╔══██╗██║     ██╔════╝[/]
[bold red]███████║[/][bold green]██████╔╝██████╔╝██║     █████╗  [/]
[bold red]██╔══██║[/][bold green]██╔═══╝ ██╔═══╝ ██║     ██╔══╝  [/]
[bold red]██║  ██║[/][bold green]██║     ██║     ███████╗███████╗[/]
[bold red]╚═╝  ╚═╝[/][bold green]╚═╝     ╚═╝     ╚══════╝╚══════╝[/]
        
[bold cyan]Music to FLAC Converter[/] [dim]v1.0.0[/]
"""
        console.print(banner)
    else:
        print("\n🍎 Apple Music to FLAC v1.0.0\n")


def print_success(message: str):
    """Print success message."""
    if RICH_AVAILABLE:
        console.print(f"[bold green]✓[/] {message}")
    else:
        print(f"✓ {message}")


def print_error(message: str):
    """Print error message."""
    if RICH_AVAILABLE:
        console.print(f"[bold red]✗[/] {message}")
    else:
        print(f"✗ {message}")


def print_info(message: str):
    """Print info message."""
    if RICH_AVAILABLE:
        console.print(f"[bold blue]ℹ[/] {message}")
    else:
        print(f"ℹ {message}")


def print_warning(message: str):
    """Print warning message."""
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠[/] {message}")
    else:
        print(f"⚠ {message}")


def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed."""
    return shutil.which("ffmpeg") is not None


def check_gamdl() -> bool:
    """Check if gamdl is available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "gamdl", "--help"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_script_dir() -> Path:
    """Get the directory where the script is located."""
    return Path(__file__).parent.resolve()


def show_cookie_instructions():
    """Display instructions for getting cookies."""
    if RICH_AVAILABLE:
        console.print()
        console.print("[bold cyan]📋 How to Get Your Cookies[/]")
        console.print()
        
        # Safari
        console.print("[bold yellow]🍎 Safari (macOS)[/]")
        console.print("   Safari doesn't support cookie extensions. Use one of these:")
        console.print("   [dim]Option A:[/] Use Chrome/Firefox just for cookie export")
        console.print("   [dim]Option B:[/] Install safari-cookies via Homebrew:")
        console.print("            [cyan]brew install nickvdyck/tap/safari-cookies[/]")
        console.print("            [cyan]safari-cookies export --domain music.apple.com > cookies.txt[/]")
        console.print()
        
        # Chrome
        console.print("[bold green]🌐 Chrome / Edge / Brave[/]")
        console.print("   1. Install: [link=https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc]Get cookies.txt LOCALLY[/]")
        console.print("   2. Go to [bold]music.apple.com[/] and log in")
        console.print("   3. Click extension → Export → Save as [bold]cookies.txt[/]")
        console.print()
        
        # Firefox
        console.print("[bold orange1]🦊 Firefox[/]")
        console.print("   1. Install: [link=https://addons.mozilla.org/addon/export-cookies-txt]Export Cookies[/]")
        console.print("   2. Go to [bold]music.apple.com[/] and log in")
        console.print("   3. Click extension → Export → Save as [bold]cookies.txt[/]")
        console.print()
        
        console.print(f"[dim]Save cookies.txt in:[/] {get_script_dir()}")
        console.print()
        console.print("[dim]⚠ Your cookies stay local. Never share them![/]")
    else:
        print("\n📋 How to Get Your Cookies:")
        print("\n🍎 Safari: Use Chrome/Firefox OR install safari-cookies via Homebrew")
        print("   brew install nickvdyck/tap/safari-cookies")
        print("   safari-cookies export --domain music.apple.com > cookies.txt")
        print("\n🌐 Chrome/Edge: Install 'Get cookies.txt LOCALLY' extension")
        print("🦊 Firefox: Install 'Export Cookies' extension")
        print("\nThen: Go to music.apple.com, log in, export cookies as 'cookies.txt'")
        print()


def check_dependencies() -> bool:
    """Check all required dependencies."""
    print_info("Checking dependencies...")
    
    all_good = True
    
    # Check FFmpeg
    if check_ffmpeg():
        print_success("FFmpeg installed")
    else:
        print_error("FFmpeg not found")
        print_info("Install with: brew install ffmpeg")
        all_good = False
    
    # Check gamdl
    if check_gamdl():
        print_success("gamdl installed")
    else:
        print_error("gamdl not found")
        print_info("Install with: pip install gamdl")
        all_good = False
    
    # Check cookies
    cookies_path = get_script_dir() / "cookies.txt"
    if cookies_path.exists():
        print_success("cookies.txt found")
    else:
        print_warning("cookies.txt not found (required for downloads)")
        all_good = False
    
    return all_good


def validate_url(url: str) -> bool:
    """Validate Apple Music URL."""
    pattern = r'https?://(www\.)?music\.apple\.com/.+'
    return bool(re.match(pattern, url))


def download_playlist(url: str, output_format: str = "aac-legacy", convert_to_flac: bool = False):
    """Download an Apple Music playlist."""
    script_dir = get_script_dir()
    downloads_dir = script_dir / "downloads"
    cookies_path = script_dir / "cookies.txt"
    
    # Check for cookies file
    if not cookies_path.exists():
        print_error("Cookies file not found!")
        show_cookie_instructions()
        sys.exit(1)
    
    # Validate URL
    if not validate_url(url):
        print_error("Invalid Apple Music URL")
        print_info("URL should look like: https://music.apple.com/us/playlist/...")
        sys.exit(1)
    
    # Create downloads directory
    downloads_dir.mkdir(exist_ok=True)
    
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            f"[bold]URL:[/] {url}\n"
            f"[bold]Format:[/] {output_format}\n"
            f"[bold]Convert to FLAC:[/] {'Yes' if convert_to_flac else 'No'}\n"
            f"[bold]Output:[/] {downloads_dir}",
            title="📥 Download Settings",
            border_style="cyan"
        ))
        console.print()
    else:
        print(f"\n📥 Downloading: {url}")
        print(f"   Format: {output_format}")
        print(f"   Output: {downloads_dir}\n")
    
    # Build gamdl command
    cmd = [
        sys.executable, "-m", "gamdl",
        "--cookies-path", str(cookies_path),
        "--output-path", str(downloads_dir),
        "--song-codec", output_format,
        "--playlist-file-template", "{playlist_title}/{track:02d} {title}",
        url
    ]
    
    print_info("Starting download... (this may take a while)")
    
    try:
        result = subprocess.run(cmd, check=True)
        print_success("Download complete!")
    except subprocess.CalledProcessError as e:
        print_error(f"Download failed with error code: {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\nDownload cancelled by user")
        sys.exit(0)
    
    # Convert to FLAC if requested
    if convert_to_flac:
        convert_directory_to_flac(downloads_dir)


def convert_directory_to_flac(directory: Path):
    """Convert all audio files in directory to FLAC format."""
    audio_extensions = {".m4a", ".mp4", ".aac"}
    audio_files = [f for f in directory.rglob("*") if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        print_warning("No audio files found to convert")
        return
    
    print_info(f"Converting {len(audio_files)} files to FLAC...")
    
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Converting...", total=len(audio_files))
            
            for audio_file in audio_files:
                flac_file = audio_file.with_suffix(".flac")
                
                if flac_file.exists():
                    progress.update(task, advance=1)
                    continue
                
                progress.update(task, description=f"Converting {audio_file.name[:30]}...")
                
                try:
                    subprocess.run(
                        [
                            "ffmpeg", "-i", str(audio_file),
                            "-c:a", "flac",
                            "-compression_level", "8",
                            "-y",  # Overwrite output
                            str(flac_file)
                        ],
                        capture_output=True,
                        check=True
                    )
                    audio_file.unlink()  # Remove original
                except subprocess.CalledProcessError:
                    pass  # Continue with other files
                
                progress.update(task, advance=1)
    else:
        for i, audio_file in enumerate(audio_files, 1):
            flac_file = audio_file.with_suffix(".flac")
            print(f"  [{i}/{len(audio_files)}] {audio_file.name}")
            
            if flac_file.exists():
                continue
            
            try:
                subprocess.run(
                    ["ffmpeg", "-i", str(audio_file), "-c:a", "flac", "-compression_level", "8", "-y", str(flac_file)],
                    capture_output=True,
                    check=True
                )
                audio_file.unlink()
            except subprocess.CalledProcessError:
                pass
    
    print_success("FLAC conversion complete!")


def main():
    parser = argparse.ArgumentParser(
        description="🍎 Download Apple Music playlists and convert to FLAC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://music.apple.com/us/playlist/..."
  %(prog)s --flac "https://music.apple.com/us/playlist/..."
  %(prog)s -f alac --flac "https://music.apple.com/us/album/..."

Supported URL types:
  • Playlists (public and library)
  • Albums
  • Songs
  • Artists (downloads all albums)

Audio formats:
  • aac-legacy  : AAC 256kbps (default, most compatible)
  • aac-he-legacy: AAC-HE 64kbps (smaller files)
  • alac        : Apple Lossless (requires wrapper setup)
        """
    )
    
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="Apple Music URL (playlist, album, or song)"
    )
    
    parser.add_argument(
        "--format", "-f",
        default="aac-legacy",
        choices=["aac-legacy", "aac-he-legacy", "alac"],
        help="Audio format to download (default: aac-legacy)"
    )
    
    parser.add_argument(
        "--flac",
        action="store_true",
        help="Convert downloaded files to FLAC format"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and exit"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Show setup instructions"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.setup:
        show_cookie_instructions()
        sys.exit(0)
    
    if args.check:
        all_good = check_dependencies()
        if all_good:
            print_success("\nAll dependencies are installed! Ready to download.")
        else:
            print_warning("\nSome dependencies are missing. Please install them first.")
        sys.exit(0 if all_good else 1)
    
    if not args.url:
        parser.print_help()
        print()
        print_info("Run with --setup to see cookie setup instructions")
        print_info("Run with --check to verify all dependencies")
        sys.exit(0)
    
    # Quick dependency check
    if not check_ffmpeg():
        print_error("FFmpeg is required but not installed")
        print_info("Install with: brew install ffmpeg")
        sys.exit(1)
    
    download_playlist(
        url=args.url,
        output_format=args.format,
        convert_to_flac=args.flac
    )
    
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold green]Done![/] Your music is ready in the [bold]downloads[/] folder.",
            border_style="green"
        ))


if __name__ == "__main__":
    main()
