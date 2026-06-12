#!/usr/bin/env bash
set -euo pipefail

PYTHON=$(command -v python3 || command -v python)

detect_distro() {
    if command -v apt &>/dev/null; then
        echo "deb"
    elif command -v dnf &>/dev/null; then
        echo "rpm"
    elif command -v yum &>/dev/null; then
        echo "rpm"
    elif command -v pacman &>/dev/null; then
        echo "arch"
    elif command -v zypper &>/dev/null; then
        echo "suse"
    else
        echo "unknown"
    fi
}

print_install_cmd() {
    local distro=$1
    case "$distro" in
        deb)    echo "sudo apt install $@" ;;
        rpm)    echo "sudo dnf install $@  (or sudo yum install $@)" ;;
        arch)   echo "sudo pacman -S $@" ;;
        suse)   echo "sudo zypper install $@" ;;
        *)      echo "Install the following packages with your package manager: $@" ;;
    esac
}

DISTRO=$(detect_distro)

echo "========================================================"
echo "          Vinetrimmer Playready 2.0 Installer"
echo "========================================================"
echo ""

# Suggest system dependencies
echo "Recommended system packages:"
case "$DISTRO" in
    deb)    echo "  sudo apt update && sudo apt install python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix ccextractor" ;;
    rpm)    echo "  sudo dnf install python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix ccextractor" ;;
    arch)   echo "  sudo pacman -S python python-pip python-virtualenv aria2 ffmpeg mkvtoolnix ccextractor" ;;
    suse)   echo "  sudo zypper install python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix ccextractor" ;;
    *)      echo "  Ensure python3, pip, aria2, ffmpeg, mkvtoolnix, ccextractor are installed" ;;
esac
echo ""

if ! command -v poetry &>/dev/null; then
    echo "Installing Poetry..."
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install poetry
else
    echo "Poetry is already installed, skipping."
fi

if [ -d ".venv" ]; then
    echo "Virtualenv already exists, skipping configuration."
else
    echo "Configuring Poetry virtualenv..."
    poetry config virtualenvs.in-project true
fi

if [ -f ".venv/bin/python" ]; then
    echo "Dependencies already installed, skipping."
else
    echo "Installing dependencies..."
    poetry install
fi

echo "Checking core binaries..."
$PYTHON -c "
import os, shutil
bins = ['aria2c','ffmpeg','ffprobe','mkvmerge','mp4decrypt','packager','ccextractor','N_m3u8DL-RE']
missing = [b for b in bins if not shutil.which(b) and not os.path.isfile(os.path.join('binaries', b))]
exit(len(missing))
" 2>/dev/null && echo "Core binaries already present, skipping." || {
    echo "Downloading core binaries..."
    $PYTHON install_binaries.py
}

echo ""
echo "Installation complete! You can now run 'poetry run vt dl -h' or use the download scripts."
echo ""
echo "Quick start:"
echo "  poetry run vt dl -h                                    # Show help"
echo "  poetry run vt dl --list AMZN B123456789                # List available tracks"
echo "  poetry run vt dl DSNP entity_id                        # Download a title"
echo "  scripts/download.Amazon.sh                             # Interactive download"
