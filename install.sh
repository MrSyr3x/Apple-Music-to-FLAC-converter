#!/bin/bash
#
# 🌊 Ripple Installer
# One-command installation for the best music downloader
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${CYAN}🌊 Ripple Installer${NC}                     ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${NC}Spotify • YouTube • Apple Music${NC}        ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Default install location
DEFAULT_INSTALL_DIR="$HOME/ripple"

# Ask for install location
echo -e "${CYAN}Where to install?${NC}"
echo -e "  Default: ${GREEN}$DEFAULT_INSTALL_DIR${NC}"
echo ""
read -p "Press Enter for default, or type path: " INSTALL_DIR

if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$DEFAULT_INSTALL_DIR"
fi

# Expand ~ to home directory
INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"

echo ""
echo -e "${BLUE}ℹ${NC} Installing to: ${GREEN}$INSTALL_DIR${NC}"

# Check if directory exists
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Directory exists. Continue? (y/n)"
    read -p "> " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo -e "${RED}✗${NC} Cancelled."
        exit 1
    fi
fi

# Create directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Check for Python
echo ""
echo -e "${BLUE}ℹ${NC} Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    echo ""
    echo "Install Python first:"
    echo "  macOS:   brew install python"
    echo "  Windows: winget install python"
    echo "  Linux:   sudo apt install python3"
    exit 1
fi

# Check for FFmpeg
echo -e "${BLUE}ℹ${NC} Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg found"
else
    echo -e "${YELLOW}⚠${NC} FFmpeg not found"
    echo ""
    echo "Install FFmpeg:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Windows: winget install ffmpeg"
    echo "  Linux:   sudo apt install ffmpeg"
    read -p "Continue anyway? (y/n): " CONT
    if [ "$CONT" != "y" ]; then
        exit 1
    fi
fi

# Download
echo ""
echo -e "${BLUE}ℹ${NC} Downloading Ripple..."
if command -v git &> /dev/null; then
    if [ -d ".git" ]; then
        git pull --quiet 2>/dev/null || true
    else
        git clone --quiet https://github.com/MrSyr3x/ripple.git . 2>/dev/null || true
    fi
else
    curl -sL https://github.com/MrSyr3x/ripple/archive/main.zip -o temp.zip 2>/dev/null
    unzip -qo temp.zip 2>/dev/null || true
    mv ripple-main/* . 2>/dev/null || true
    rm -rf ripple-main temp.zip 2>/dev/null || true
fi
echo -e "${GREEN}✓${NC} Downloaded"

# Create virtual environment
echo ""
echo -e "${BLUE}ℹ${NC} Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}ℹ${NC} Installing packages..."
pip install --quiet --upgrade pip 2>/dev/null
pip install --quiet -r requirements.txt 2>/dev/null
echo -e "${GREEN}✓${NC} Packages installed"

# Make scripts executable
chmod +x start.sh 2>/dev/null || true
chmod +x uninstall.sh 2>/dev/null || true

# Create global command
echo ""
echo -e "${BLUE}ℹ${NC} Creating 'ripple' command..."

SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"

if ! grep -q "alias ripple=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Ripple Music Downloader" >> "$SHELL_RC"
    echo "alias ripple='cd $INSTALL_DIR && source venv/bin/activate && python download.py'" >> "$SHELL_RC"
fi
echo -e "${GREEN}✓${NC} Added 'ripple' command"

# Deactivate venv for now
deactivate 2>/dev/null || true

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✓ Installation Complete!${NC}                ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Installed to:${NC} $INSTALL_DIR"
echo ""
echo -e "  ${CYAN}To start now:${NC}"
echo -e "    cd $INSTALL_DIR && ./start.sh"
echo ""
echo -e "  ${CYAN}Or restart terminal and use:${NC}"
echo -e "    ripple"
echo ""

# Ask if user wants to start now
read -p "Start Ripple now? (y/n): " START_NOW

if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    echo ""
    source venv/bin/activate
    python download.py
else
    echo ""
    echo -e "${GREEN}✓${NC} Run later with: ${CYAN}ripple${NC} or ${CYAN}./start.sh${NC}"
    echo ""
fi
