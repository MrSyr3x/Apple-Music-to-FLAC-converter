#!/bin/bash
#
# 🎵 Music Downloader Uninstaller
# Cleanly removes the Music Downloader
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🎵 Music Downloader Uninstaller${NC}"
echo ""

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${YELLOW}⚠${NC} This will remove:"
echo "  • Virtual environment (venv/)"
echo "  • Cache files"
echo "  • The 'music-dl' alias from your shell"
echo ""
echo -e "${BLUE}ℹ${NC} Your downloaded music in 'downloads/' will be kept."
echo ""
read -p "Are you sure you want to uninstall? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${GREEN}✓${NC} Uninstall cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}ℹ${NC} Removing virtual environment..."
rm -rf "$INSTALL_DIR/venv"

echo -e "${BLUE}ℹ${NC} Removing cache files..."
rm -rf "$INSTALL_DIR/__pycache__"
rm -rf "$INSTALL_DIR/music_downloader/__pycache__"
rm -rf "$INSTALL_DIR/music_downloader/platforms/__pycache__"
rm -rf "$INSTALL_DIR/.spotdl-cache"
rm -rf "$INSTALL_DIR/downloads/.spotdl-cache"

echo -e "${BLUE}ℹ${NC} Removing shell alias..."
SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"

# Remove the alias lines
if [ -f "$SHELL_RC" ]; then
    # Create temp file without the music-dl lines
    grep -v "# Music Downloader" "$SHELL_RC" | grep -v "alias music-dl=" > "${SHELL_RC}.tmp"
    mv "${SHELL_RC}.tmp" "$SHELL_RC"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✓ Uninstall Complete!${NC}                   ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}What was removed:${NC}"
echo "    • Python virtual environment"
echo "    • Cache files"
echo "    • 'music-dl' command"
echo ""
echo -e "  ${CYAN}What was kept:${NC}"
echo "    • Your downloaded music"
echo "    • The program files (delete $INSTALL_DIR manually if needed)"
echo ""
echo -e "  ${CYAN}To completely remove:${NC}"
echo "    rm -rf $INSTALL_DIR"
echo ""

read -p "Delete the entire program folder? (y/n): " DELETE_ALL

if [ "$DELETE_ALL" = "y" ] || [ "$DELETE_ALL" = "Y" ]; then
    echo ""
    echo -e "${YELLOW}⚠${NC} Keeping your downloads folder..."
    
    # Move downloads out if exists
    if [ -d "$INSTALL_DIR/downloads" ] && [ "$(ls -A $INSTALL_DIR/downloads 2>/dev/null)" ]; then
        DOWNLOADS_BACKUP="$HOME/Music-Downloader-Downloads"
        mv "$INSTALL_DIR/downloads" "$DOWNLOADS_BACKUP"
        echo -e "${GREEN}✓${NC} Downloads moved to: $DOWNLOADS_BACKUP"
    fi
    
    cd "$HOME"
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓${NC} Program folder removed"
    echo ""
fi
