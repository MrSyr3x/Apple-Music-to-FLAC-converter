"""
Metadata verification utility
Scans downloaded files to check for missing or mismatched metadata
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Try to import mutagen for metadata reading
try:
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.oggvorbis import OggVorbis
    from mutagen.oggopus import OggOpus
    from mutagen.wave import WAVE
    from mutagen.id3 import ID3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


def _get_audio_metadata(file_path: Path) -> Dict:
    """Extract metadata from an audio file."""
    if not MUTAGEN_AVAILABLE:
        return {"error": "mutagen not installed"}
    
    result = {
        "title": None,
        "artist": None,
        "album": None,
        "has_artwork": False,
        "artwork_size": 0,
    }
    
    try:
        suffix = file_path.suffix.lower()
        
        if suffix == ".flac":
            audio = FLAC(file_path)
            result["title"] = audio.get("title", [None])[0]
            result["artist"] = audio.get("artist", [None])[0]
            result["album"] = audio.get("album", [None])[0]
            if audio.pictures:
                result["has_artwork"] = True
                result["artwork_size"] = len(audio.pictures[0].data)
        
        elif suffix == ".mp3":
            audio = MP3(file_path)
            if audio.tags:
                result["title"] = str(audio.tags.get("TIT2", ""))
                result["artist"] = str(audio.tags.get("TPE1", ""))
                result["album"] = str(audio.tags.get("TALB", ""))
                # Check for embedded picture
                for tag in audio.tags.values():
                    if tag.FrameID == "APIC":
                        result["has_artwork"] = True
                        result["artwork_size"] = len(tag.data)
                        break
        
        elif suffix in [".m4a", ".mp4"]:
            audio = MP4(file_path)
            result["title"] = audio.tags.get("\xa9nam", [None])[0] if audio.tags else None
            result["artist"] = audio.tags.get("\xa9ART", [None])[0] if audio.tags else None
            result["album"] = audio.tags.get("\xa9alb", [None])[0] if audio.tags else None
            if audio.tags and "covr" in audio.tags:
                result["has_artwork"] = True
                result["artwork_size"] = len(audio.tags["covr"][0])
        
        elif suffix == ".ogg":
            audio = OggVorbis(file_path)
            result["title"] = audio.get("title", [None])[0]
            result["artist"] = audio.get("artist", [None])[0]
            result["album"] = audio.get("album", [None])[0]
            if "metadata_block_picture" in audio:
                result["has_artwork"] = True
        
        elif suffix == ".opus":
            audio = OggOpus(file_path)
            result["title"] = audio.get("title", [None])[0]
            result["artist"] = audio.get("artist", [None])[0]
            result["album"] = audio.get("album", [None])[0]
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def scan_downloads(downloads_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Scan all downloaded audio files for metadata issues.
    
    Returns:
        Tuple of (files_ok, files_with_issues)
    """
    audio_extensions = {".flac", ".mp3", ".m4a", ".mp4", ".ogg", ".opus", ".wav"}
    files_ok = []
    files_with_issues = []
    
    for file_path in downloads_dir.rglob("*"):
        if file_path.suffix.lower() not in audio_extensions:
            continue
        
        metadata = _get_audio_metadata(file_path)
        
        issues = []
        
        # Check for missing metadata
        if not metadata.get("title"):
            issues.append("missing title")
        if not metadata.get("artist"):
            issues.append("missing artist")
        if not metadata.get("has_artwork"):
            issues.append("missing artwork")
        if metadata.get("error"):
            issues.append(metadata["error"])
        
        file_info = {
            "path": file_path,
            "name": file_path.name,
            "metadata": metadata,
            "issues": issues
        }
        
        if issues:
            files_with_issues.append(file_info)
        else:
            files_ok.append(file_info)
    
    return files_ok, files_with_issues


def print_scan_results(files_ok: List[Dict], files_with_issues: List[Dict]):
    """Print scan results in a clean format."""
    total = len(files_ok) + len(files_with_issues)
    
    print(f"\n  📊 Metadata Scan Results")
    print(f"  {'─' * 40}")
    print(f"  ✓ {len(files_ok)} files OK")
    print(f"  ⚠ {len(files_with_issues)} files with issues")
    print()
    
    if files_with_issues:
        print("  Files with issues:")
        for f in files_with_issues[:20]:  # Show first 20
            issues_str = ", ".join(f["issues"])
            name = f["name"]
            if len(name) > 40:
                name = name[:37] + "..."
            print(f"    • {name}")
            print(f"      └─ {issues_str}")
        
        if len(files_with_issues) > 20:
            print(f"    ... and {len(files_with_issues) - 20} more")
        print()
    
    return len(files_with_issues) == 0


def verify_downloads_interactive(downloads_dir: Path) -> bool:
    """Run verification and provide interactive options."""
    if not MUTAGEN_AVAILABLE:
        print("  ⚠ Install mutagen for metadata verification: pip install mutagen")
        return True
    
    print("\n  🔍 Scanning downloaded files...")
    files_ok, files_with_issues = scan_downloads(downloads_dir)
    
    if not files_ok and not files_with_issues:
        print("  ℹ No audio files found to scan")
        return True
    
    print_scan_results(files_ok, files_with_issues)
    
    return len(files_with_issues) == 0
