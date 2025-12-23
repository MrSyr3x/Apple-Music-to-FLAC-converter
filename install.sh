#!/bin/bash
#
# 🎵 Music Downloader Installer
# One-command installation for Apple Music, Spotify, and YouTube downloads
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${MAGENTA}╔══════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║${NC}  ${CYAN}🎵 Music Downloader Installer${NC}           ${MAGENTA}║${NC}"
echo -e "${MAGENTA}║${NC}  ${NC}Apple Music • Spotify • YouTube${NC}        ${MAGENTA}║${NC}"
echo -e "${MAGENTA}╚══════════════════════════════════════════╝${NC}"
echo ""

# Default install location
DEFAULT_INSTALL_DIR="$HOME/music-downloader"

# Ask for install location
echo -e "${CYAN}Where would you like to install?${NC}"
echo -e "${NC}  Default: ${GREEN}$DEFAULT_INSTALL_DIR${NC}"
echo ""
read -p "Press Enter for default, or type a path: " INSTALL_DIR

if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$DEFAULT_INSTALL_DIR"
fi

# Expand ~ to home directory
INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"

echo ""
echo -e "${BLUE}ℹ${NC} Installing to: ${GREEN}$INSTALL_DIR${NC}"

# Check if directory exists
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Directory already exists. Files may be overwritten."
    read -p "Continue? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo -e "${RED}✗${NC} Installation cancelled."
        exit 1
    fi
fi

# Create directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Check for Python 3.10+
echo ""
echo -e "${BLUE}ℹ${NC} Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

# Check for FFmpeg
echo -e "${BLUE}ℹ${NC} Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg found"
else
    echo -e "${YELLOW}⚠${NC} FFmpeg not found. Installing with Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
        echo -e "${GREEN}✓${NC} FFmpeg installed"
    else
        echo -e "${RED}✗${NC} Please install FFmpeg manually: brew install ffmpeg"
        exit 1
    fi
fi

# Clone or download the project
echo ""
echo -e "${BLUE}ℹ${NC} Downloading Music Downloader..."

if command -v git &> /dev/null; then
    if [ -d ".git" ]; then
        git pull --quiet
    else
        git clone --quiet https://github.com/syr3x/apple-music-to-flac.git .
    fi
    echo -e "${GREEN}✓${NC} Downloaded"
else
    echo -e "${YELLOW}⚠${NC} Git not found. Downloading as ZIP..."
    curl -sL https://github.com/syr3x/apple-music-to-flac/archive/main.zip -o temp.zip
    unzip -qo temp.zip
    mv apple-music-to-flac-main/* . 2>/dev/null || true
    rm -rf apple-music-to-flac-main temp.zip
    echo -e "${GREEN}✓${NC} Downloaded"
fi

# Create virtual environment
echo ""
echo -e "${BLUE}ℹ${NC} Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}ℹ${NC} Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Make scripts executable
chmod +x start.sh 2>/dev/null || true
chmod +x uninstall.sh 2>/dev/null || true

# Create a global command
echo ""
echo -e "${BLUE}ℹ${NC} Creating global command..."
SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"

# Add alias if not exists
if ! grep -q "alias music-dl=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Music Downloader" >> "$SHELL_RC"
    echo "alias music-dl='cd $INSTALL_DIR && ./start.sh'" >> "$SHELL_RC"
    echo -e "${GREEN}✓${NC} Added 'music-dl' command to your shell"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✓ Installation Complete!${NC}                ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Installed to:${NC} $INSTALL_DIR"
echo ""
echo -e "  ${CYAN}To start:${NC}"
echo -e "    cd $INSTALL_DIR && ./start.sh"
echo ""
echo -e "  ${CYAN}Or restart your terminal and use:${NC}"
echo -e "    music-dl"
echo ""
echo -e "  ${CYAN}To uninstall:${NC}"
echo -e "    cd $INSTALL_DIR && ./uninstall.sh"
echo ""

# Ask if user wants to start now
read -p "Would you like to start the Music Downloader now? (y/n): " START_NOW

if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    echo ""
    ./start.sh
else
    echo ""
    echo -e "${GREEN}✓${NC} You can start later with: ${CYAN}cd $INSTALL_DIR && ./start.sh${NC}"
    echo -e "${NC}  Or just type: ${CYAN}music-dl${NC} (after restarting terminal)"
    echo ""
fi
