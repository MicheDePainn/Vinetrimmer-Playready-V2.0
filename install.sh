#!/usr/bin/env bash
set -euo pipefail

if [ "$EUID" -eq 0 ]; then
    echo "Erreur : Ce script ne doit pas être exécuté en tant que root (sudo)."
    echo "L'exécution avec sudo attribue la propriété du dossier .venv à root, ce qui bloquera les installations futures."
    echo "Relancez le script en tant qu'utilisateur standard (ex: ./install.sh)."
    exit 1
fi

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

echo "Recommended system packages:"
case "$DISTRO" in
    deb)    echo "  sudo apt update && sudo apt install python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix curl libffi-dev libssl-dev python3-dev libxml2-dev libxslt1-dev libmediainfo0v5 pipx" ;;
    rpm)    echo "  sudo dnf install python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix curl libffi-devel openssl-devel python3-devel libxml2-devel libxslt-devel libmediainfo pipx" ;;
    arch)   echo "  sudo pacman -S python python-pip python-virtualenv aria2 ffmpeg mkvtoolnix curl libffi openssl libxml2 libxslt libmediainfo python-pipx" ;;
    suse)   echo "  sudo zypper install python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix curl libffi-devel libopenssl-devel python3-devel libxml2-devel libxslt1-devel libmediainfo pipx" ;;
    *)      echo "  Ensure python3, pip, aria2, ffmpeg, mkvtoolnix, and C-development headers are installed" ;;
esac
echo ""

if ! command -v poetry &>/dev/null; then
    echo "Installing Poetry..."
    if [ "$DISTRO" = "deb" ]; then
        echo "Using pipx for Debian-based systems to comply with PEP 668..."
        pipx ensurepath
        pipx install poetry
        export PATH="$HOME/.local/bin:$PATH"
    else
        $PYTHON -m pip install --upgrade pip
        $PYTHON -m pip install poetry || $PYTHON -m pip install poetry --break-system-packages
    fi
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
    export CFLAGS="-Wno-incompatible-pointer-types"
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
echo "  poetry run vt dl -h"
echo "  poetry run vt dl --list AMZN B123456789"
echo "  poetry run vt dl DSNP entity_id"
echo "  scripts/download.Amazon.sh"