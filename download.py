#!/usr/bin/env python3
"""
🎵 Music Downloader
Multi-platform music downloader with interactive TUI
https://github.com/MrSyr3x/Apple-Music-to-FLAC-converter
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="🎵 Multi-platform Music Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Run without arguments to start the interactive TUI.

Supported platforms:
  • Apple Music (requires cookies)
  • Spotify (no login needed)
  • YouTube Music (no login needed)

Examples:
  %(prog)s                    # Start interactive TUI
  %(prog)s --help             # Show this help
        """
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Music Downloader v2.0.0"
    )
    
    args = parser.parse_args()
    
    # Import and run TUI
    try:
        from music_downloader.tui import run_tui
        run_tui()
    except KeyboardInterrupt:
        print("\n\nCancelled by user. Goodbye! 👋")
        sys.exit(0)
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
