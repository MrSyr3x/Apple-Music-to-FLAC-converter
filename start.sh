#!/bin/bash
#
# 🌊 Ripple - Start Script
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Setting up first time..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet -r requirements.txt
fi

# Run the downloader
python download.py
