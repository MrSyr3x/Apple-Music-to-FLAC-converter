"""
Configuration management for Ripple
Saves user preferences like default format, download location, etc.
"""

import json
from pathlib import Path
from typing import Optional, Any, Dict


# Default configuration
DEFAULT_CONFIG = {
    "default_format": "mp3",
    "default_platform": None,  # None = ask every time
    "download_location": None,  # None = use default
    "apple_music": {
        "default_codec": "aac-legacy",
        "include_lyrics": False,
    },
    "spotify": {
        "default_format": "mp3",
    },
    "youtube": {
        "default_format": "mp3",
    },
    "ui": {
        "show_speed": True,
        "colored_output": True,
    }
}


def get_config_dir() -> Path:
    """Get the config directory path."""
    config_dir = Path.home() / ".ripple"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the config file path."""
    return get_config_dir() / "config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from file, or return defaults."""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                saved_config = json.load(f)
                # Merge with defaults (in case new options were added)
                return {**DEFAULT_CONFIG, **saved_config}
        except (json.JSONDecodeError, IOError):
            pass
    
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value."""
    config = load_config()
    
    # Support nested keys like "apple_music.default_codec"
    keys = key.split(".")
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def set_setting(key: str, value: Any) -> bool:
    """Set a specific setting value."""
    config = load_config()
    
    # Support nested keys like "apple_music.default_codec"
    keys = key.split(".")
    current = config
    
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    current[keys[-1]] = value
    return save_config(config)


def get_last_download_location() -> Optional[Path]:
    """Get the last used download location."""
    location = get_setting("download_location")
    if location and Path(location).exists():
        return Path(location)
    return None


def save_last_download_location(path: Path) -> bool:
    """Save the last used download location."""
    return set_setting("download_location", str(path))


def get_default_format(platform: str) -> str:
    """Get the default format for a platform."""
    platform_format = get_setting(f"{platform}.default_format")
    if platform_format:
        return platform_format
    return get_setting("default_format", "mp3")


def save_default_format(platform: str, format: str) -> bool:
    """Save the default format for a platform."""
    return set_setting(f"{platform}.default_format", format)


def reset_config() -> bool:
    """Reset configuration to defaults."""
    return save_config(DEFAULT_CONFIG.copy())


# Quick access functions
def should_show_speed() -> bool:
    return get_setting("ui.show_speed", True)


def should_use_colors() -> bool:
    return get_setting("ui.colored_output", True)
