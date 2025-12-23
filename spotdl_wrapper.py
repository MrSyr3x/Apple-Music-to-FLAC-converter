#!/usr/bin/env python3
"""
Spotdl wrapper that fixes Python 3.14 asyncio compatibility
and ensures file descriptor limits are sufficient for large playlists.
"""

import asyncio
import sys
import resource

# Ensure file descriptor limit is sufficient for large playlists
# macOS default can sometimes be limited in certain terminal contexts
try:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    # Only increase if current soft limit is low
    if soft < 4096:
        new_limit = min(4096, hard)
        resource.setrlimit(resource.RLIMIT_NOFILE, (new_limit, hard))
except (ValueError, resource.error):
    pass  # Can't change limit, continue anyway

# Fix for Python 3.14+: Create event loop before importing spotdl
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Now import and run spotdl
from spotdl.console import console_entry_point

if __name__ == "__main__":
    console_entry_point()
