"""
Tidal Downloader for Ripple
Downloads tracks from Tidal using public APIs
Ported from SpotiFLAC (Go) to Python
"""

import json
import os
import re
import time
import requests
from pathlib import Path
from typing import Optional, Tuple, List
from urllib.parse import quote


class TidalDownloader:
    """Downloads tracks from Tidal via third-party API mirrors."""
    
    def __init__(self):
        # Tidal API credentials (public client - decoded from base64)
        self.client_id = "6BDSRdpK9hqEBTgU"
        self.client_secret = "xeuPmY7nbpZ9IIbLAcQ93shka1VNheUAqN6IcszjTG8="
        
        # Third-party API endpoints (multiple for redundancy)
        self.api_endpoints = [
            "https://vogel.qqdl.site",
            "https://maus.qqdl.site",
            "https://hund.qqdl.site",
            "https://katze.qqdl.site",
            "https://wolf.qqdl.site",
            "https://tidal.kinoplus.online",
            "https://tidal-api.binimum.org",
            "https://triton.squid.wtf",
        ]
        
        self.session = requests.Session()
        self.session.timeout = 30
        self._access_token = None
        self._token_expires = 0
    
    def get_access_token(self) -> str:
        """Get Tidal API access token."""
        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expires:
            return self._access_token
        
        try:
            resp = self.session.post(
                "https://auth.tidal.com/v1/oauth2/token",
                data=f"client_id={self.client_id}&grant_type=client_credentials",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=(self.client_id, self.client_secret),
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data["access_token"]
            # Token expires in ~24 hours, cache for 23 hours
            self._token_expires = time.time() + 82800
            return self._access_token
        except Exception as e:
            raise RuntimeError(f"Failed to get Tidal access token: {e}")
    
    def search_by_isrc(self, isrc: str) -> Optional[dict]:
        """Search for a track on Tidal by ISRC."""
        token = self.get_access_token()
        
        try:
            resp = self.session.get(
                f"https://api.tidal.com/v1/search/tracks?query={quote(isrc)}&limit=10&offset=0&countryCode=US",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Find exact ISRC match
            for track in data.get("items", []):
                if track.get("isrc") == isrc:
                    return track
            
            # Return first result if no exact match
            if data.get("items"):
                return data["items"][0]
            
            return None
        except Exception as e:
            print(f"  ⚠ Tidal search failed: {e}")
            return None
    
    def search_by_query(self, artist: str, title: str) -> Optional[dict]:
        """Search for a track on Tidal by artist and title."""
        token = self.get_access_token()
        query = f"{artist} {title}"
        
        try:
            resp = self.session.get(
                f"https://api.tidal.com/v1/search/tracks?query={quote(query)}&limit=10&offset=0&countryCode=US",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("items"):
                return data["items"][0]
            
            return None
        except Exception as e:
            print(f"  ⚠ Tidal search failed: {e}")
            return None
    
    def get_download_url(self, track_id: int, quality: str = "LOSSLESS") -> Optional[str]:
        """Get download URL from third-party API mirrors."""
        for api_url in self.api_endpoints:
            try:
                url = f"{api_url}/track/?id={track_id}&quality={quality}"
                resp = self.session.get(url, timeout=15)
                
                if resp.status_code != 200:
                    continue
                
                data = resp.json()
                
                # Handle v2 format (manifest)
                if isinstance(data, dict) and "data" in data:
                    manifest = data["data"].get("manifest")
                    if manifest:
                        # Decode manifest to get URL
                        import base64
                        manifest_data = json.loads(base64.b64decode(manifest))
                        if "urls" in manifest_data:
                            return manifest_data["urls"][0]
                
                # Handle v1 format (array with OriginalTrackUrl)
                if isinstance(data, list):
                    for item in data:
                        if "OriginalTrackUrl" in item:
                            return item["OriginalTrackUrl"]
                
            except Exception:
                continue
        
        return None
    
    def download_file(self, url: str, output_path: Path) -> bool:
        """Download file from URL with progress."""
        try:
            resp = self.session.get(url, stream=True, timeout=120)
            resp.raise_for_status()
            
            total_size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            return True
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            if output_path.exists():
                output_path.unlink()
            return False
    
    def download_track(
        self,
        isrc: str,
        output_dir: Path,
        filename: str,
        artist: str = "",
        title: str = ""
    ) -> Tuple[bool, str]:
        """
        Download a track from Tidal.
        
        Returns: (success, filepath or error message)
        """
        # Search for track
        track = self.search_by_isrc(isrc)
        
        if not track and artist and title:
            track = self.search_by_query(artist, title)
        
        if not track:
            return False, f"Track not found on Tidal: {artist} - {title}"
        
        track_id = track.get("id")
        if not track_id:
            return False, "Invalid track data from Tidal"
        
        # Get download URL
        download_url = self.get_download_url(track_id)
        
        if not download_url:
            return False, "No download URL available from any API"
        
        # Determine file extension
        extension = ".flac"
        if "mp4" in download_url.lower() or "m4a" in download_url.lower():
            extension = ".m4a"
        
        # Create output path
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        output_path = output_dir / f"{safe_filename}{extension}"
        
        # Skip if already exists
        if output_path.exists():
            return True, str(output_path)
        
        # Download
        success = self.download_file(download_url, output_path)
        
        if success:
            return True, str(output_path)
        else:
            return False, "Download failed"


class SpotifyToTidal:
    """Bridge to convert Spotify tracks to Tidal downloads."""
    
    def __init__(self):
        self.tidal = TidalDownloader()
        self.session = requests.Session()
    
    def get_spotify_track_info(self, spotify_url: str) -> Optional[dict]:
        """Get track info from song.link API."""
        try:
            resp = self.session.get(
                f"https://api.song.link/v1-alpha.1/links?url={quote(spotify_url)}",
                timeout=15
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
    
    def download_from_spotify_url(
        self,
        spotify_url: str,
        output_dir: Path,
        on_progress: callable = None
    ) -> Tuple[bool, str]:
        """
        Download a Spotify track via Tidal.
        
        Returns: (success, filepath or error message)
        """
        # Get song.link data
        songlink_data = self.get_spotify_track_info(spotify_url)
        
        if not songlink_data:
            return False, "Failed to get track info from song.link"
        
        # Extract metadata
        entities = songlink_data.get("entitiesByUniqueId", {})
        spotify_entity = None
        tidal_url = None
        
        # Find Spotify entity for metadata
        for key, entity in entities.items():
            if "spotify" in key.lower():
                spotify_entity = entity
            if "tidal" in key.lower():
                tidal_url = songlink_data.get("linksByPlatform", {}).get("tidal", {}).get("url")
        
        if not spotify_entity:
            return False, "Could not find track metadata"
        
        title = spotify_entity.get("title", "Unknown")
        artist = spotify_entity.get("artistName", "Unknown")
        
        # Try to get ISRC from Tidal entity
        isrc = None
        for key, entity in entities.items():
            if "tidal" in key.lower():
                # ISRC is part of the ID pattern
                isrc_match = re.search(r'::([A-Z]{2}[A-Z0-9]{10})', key)
                if isrc_match:
                    isrc = isrc_match.group(1)
                break
        
        # Extract Tidal track ID from URL if available
        tidal_track_id = None
        if tidal_url:
            match = re.search(r'/track/(\d+)', tidal_url)
            if match:
                tidal_track_id = int(match.group(1))
        
        # If we have the Tidal track ID directly, use it
        if tidal_track_id:
            download_url = self.tidal.get_download_url(tidal_track_id)
            if download_url:
                output_dir.mkdir(parents=True, exist_ok=True)
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', f"{title} - {artist}")
                
                extension = ".flac"
                if "mp4" in download_url.lower() or "m4a" in download_url.lower():
                    extension = ".m4a"
                
                output_path = output_dir / f"{safe_filename}{extension}"
                
                if output_path.exists():
                    return True, str(output_path)
                
                success = self.tidal.download_file(download_url, output_path)
                if success:
                    return True, str(output_path)
        
        # Fallback to ISRC search
        if isrc:
            return self.tidal.download_track(
                isrc=isrc,
                output_dir=output_dir,
                filename=f"{title} - {artist}",
                artist=artist,
                title=title
            )
        
        # Final fallback: search by name
        return self.tidal.download_track(
            isrc="",
            output_dir=output_dir,
            filename=f"{title} - {artist}",
            artist=artist,
            title=title
        )


# Test function
def test_tidal():
    """Test the Tidal downloader."""
    downloader = TidalDownloader()
    
    # Test getting access token
    try:
        token = downloader.get_access_token()
        print(f"✓ Got access token: {token[:20]}...")
    except Exception as e:
        print(f"✗ Failed to get token: {e}")
        return
    
    # Test searching
    track = downloader.search_by_isrc("USUM71703861")  # Shape of You
    if track:
        print(f"✓ Found track: {track.get('title')} by {track.get('artist', {}).get('name')}")
        
        # Test getting download URL
        download_url = downloader.get_download_url(track.get("id"))
        if download_url:
            print(f"✓ Got download URL: {download_url[:50]}...")
        else:
            print("✗ Could not get download URL")
    else:
        print("✗ Track not found")


if __name__ == "__main__":
    test_tidal()
