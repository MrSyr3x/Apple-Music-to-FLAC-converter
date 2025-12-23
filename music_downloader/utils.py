"""
Utility functions for music downloader
- Cookie finding
- File cleanup
- Path handling
"""

import os
import glob
from pathlib import Path
from typing import List, Optional


def find_cookie_files(search_dirs: Optional[List[str]] = None) -> List[Path]:
    """
    Search for cookie files in common locations.
    
    Returns list of found cookie files sorted by modification time (newest first).
    """
    if search_dirs is None:
        search_dirs = [
            ".",  # Current directory
            str(Path.home() / "Downloads"),  # ~/Downloads
            str(Path.home() / "Desktop"),  # ~/Desktop
        ]
    
    patterns = [
        "*cookie*.txt",
        "*cookies*.txt", 
        "cookies.txt",
    ]
    
    found_files = []
    
    for directory in search_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
            
        for pattern in patterns:
            matches = list(dir_path.glob(pattern))
            found_files.extend(matches)
    
    # Remove duplicates and sort by modification time (newest first)
    unique_files = list(set(found_files))
    unique_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return unique_files


def get_project_dir() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


def get_downloads_dir() -> Path:
    """Get the downloads directory."""
    downloads = get_project_dir() / "downloads"
    downloads.mkdir(exist_ok=True)
    return downloads


def delete_file_safely(file_path: Path) -> bool:
    """
    Safely delete a file.
    
    Returns True if deleted, False otherwise.
    """
    try:
        if file_path.exists():
            file_path.unlink()
            return True
    except Exception:
        pass
    return False


def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()


def flatten_downloads(downloads_dir: Path) -> int:
    """
    Move all audio files to root of downloads directory.
    Removes empty subdirectories after.
    
    Returns count of files moved.
    """
    audio_extensions = {'.flac', '.m4a', '.mp3', '.aac', '.wav', '.ogg'}
    moved_count = 0
    
    # Find all audio files in subdirectories
    for audio_file in downloads_dir.rglob('*'):
        if audio_file.suffix.lower() in audio_extensions:
            if audio_file.parent != downloads_dir:
                # File is in a subdirectory, move it
                new_path = downloads_dir / audio_file.name
                
                # Handle name conflicts
                if new_path.exists():
                    base = audio_file.stem
                    ext = audio_file.suffix
                    counter = 1
                    while new_path.exists():
                        new_path = downloads_dir / f"{base}_{counter}{ext}"
                        counter += 1
                
                audio_file.rename(new_path)
                moved_count += 1
    
    # Remove empty directories
    for dirpath in sorted(downloads_dir.rglob('*'), reverse=True):
        if dirpath.is_dir():
            try:
                dirpath.rmdir()  # Only removes if empty
            except OSError:
                pass  # Directory not empty
    
    return moved_count


def delete_lyrics_files(downloads_dir: Path) -> int:
    """
    Delete all lyrics files (.lrc, .srt, .ttml).
    
    Returns count of files deleted.
    """
    lyrics_extensions = {'.lrc', '.srt', '.ttml'}
    deleted_count = 0
    
    for lyrics_file in downloads_dir.rglob('*'):
        if lyrics_file.suffix.lower() in lyrics_extensions:
            if delete_file_safely(lyrics_file):
                deleted_count += 1
    
    return deleted_count
