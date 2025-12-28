#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print step
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    print_step "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the downloader
# We use 'exec' so the shell process is replaced by python, 
# but since we want to deactivate after, we just run it normally.
python3 download.py

# Deactivate is technically not needed as the script ends, 
# but good practice if sourced.
deactivate
