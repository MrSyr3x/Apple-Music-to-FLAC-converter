#!/bin/bash
#
# 🌊 Ripple Uninstaller
#

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🌊 Ripple Uninstaller${NC}"
echo ""

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${YELLOW}⚠${NC} This will remove:"
echo "  • Virtual environment"
echo "  • Cache files"
echo "  • 'ripple' command"
echo ""
echo -e "${BLUE}ℹ${NC} Your downloads will be kept."
echo ""
read -p "Uninstall? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${GREEN}✓${NC} Cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}ℹ${NC} Removing virtual environment..."
rm -rf "$INSTALL_DIR/venv"

echo -e "${BLUE}ℹ${NC} Removing cache..."
rm -rf "$INSTALL_DIR/__pycache__"
rm -rf "$INSTALL_DIR/music_downloader/__pycache__"
rm -rf "$INSTALL_DIR/music_downloader/platforms/__pycache__"
rm -rf "$INSTALL_DIR/.spotdl-cache"
rm -rf "$INSTALL_DIR/downloads/.spotdl-cache"

echo -e "${BLUE}ℹ${NC} Removing shell command..."
SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"

if [ -f "$SHELL_RC" ]; then
    grep -v "# Ripple" "$SHELL_RC" | grep -v "alias ripple=" > "${SHELL_RC}.tmp"
    mv "${SHELL_RC}.tmp" "$SHELL_RC"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✓ Uninstalled${NC}                          ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Downloads kept at: ${CYAN}$INSTALL_DIR/downloads${NC}"
echo ""

read -p "Delete entire folder? (y/n): " DELETE_ALL

if [ "$DELETE_ALL" = "y" ] || [ "$DELETE_ALL" = "Y" ]; then
    if [ -d "$INSTALL_DIR/downloads" ] && [ "$(ls -A $INSTALL_DIR/downloads 2>/dev/null)" ]; then
        BACKUP="$HOME/Ripple-Downloads"
        mv "$INSTALL_DIR/downloads" "$BACKUP"
        echo -e "${GREEN}✓${NC} Downloads moved to: $BACKUP"
    fi
    
    cd "$HOME"
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓${NC} Folder removed"
fi

echo ""
