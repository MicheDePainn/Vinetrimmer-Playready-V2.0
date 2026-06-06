#!/usr/bin/env bash
set -euo pipefail

PYTHON=$(command -v python3 || command -v python)
SYSTEM_DEPS="python3 python3-pip python3-venv aria2 ffmpeg mkvtoolnix"

echo "========================================================"
echo "          Vinetrimmer Playready 2.0 Installer"
echo "========================================================"
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
