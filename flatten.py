#!/usr/bin/env python3
"""
Flatten Downloads folder to simple structure:
- All audio files moved directly to Downloads/
- Optional: specify playlist name to create subfolder
"""

import sys
import shutil
from pathlib import Path

def flatten_folder(source_dir: Path, playlist_name: str = None):
    """Move all audio files to flat structure."""
    
    audio_extensions = ['.m4a', '.flac', '.mp3', '.opus', '.aac']
    
    # Find all audio files recursively
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(source_dir.rglob(f'*{ext}'))
    
    # Also include lyrics files
    lrc_files = list(source_dir.rglob('*.lrc'))
    
    if playlist_name:
        target_dir = source_dir / playlist_name
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = source_dir
    
    moved_audio = 0
    moved_lrc = 0
    
    # Move audio files
    for audio_file in audio_files:
        # Skip files already in target directory (top level)
        if audio_file.parent == target_dir:
            continue
            
        target_path = target_dir / audio_file.name
        
        # Handle duplicates
        if target_path.exists():
            stem = audio_file.stem
            suffix = audio_file.suffix
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
        
        shutil.move(str(audio_file), str(target_path))
        moved_audio += 1
        print(f"✓ {audio_file.name}")
    
    # Move lyrics files
    for lrc_file in lrc_files:
        if lrc_file.parent == target_dir:
            continue
            
        target_path = target_dir / lrc_file.name
        if target_path.exists():
            stem = lrc_file.stem
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}.lrc"
                counter += 1
        
        shutil.move(str(lrc_file), str(target_path))
        moved_lrc += 1
    
    # Clean up empty directories
    for item in sorted(source_dir.rglob('*'), reverse=True):
        if item.is_dir() and item != target_dir:
            try:
                item.rmdir()  # Only removes if empty
            except OSError:
                pass  # Not empty, skip
    
    print(f"\n✅ Moved {moved_audio} audio files, {moved_lrc} lyrics files")
    if playlist_name:
        print(f"   → {target_dir}/")
    else:
        print(f"   → {source_dir}/")

if __name__ == "__main__":
    downloads = Path(__file__).parent / "Downloads"
    
    if not downloads.exists():
        print("❌ Downloads folder not found")
        sys.exit(1)
    
    playlist_name = None
    if len(sys.argv) > 1:
        playlist_name = " ".join(sys.argv[1:])
        print(f"📁 Flattening to: Downloads/{playlist_name}/")
    else:
        print("📁 Flattening to: Downloads/")
    
    flatten_folder(downloads, playlist_name)
