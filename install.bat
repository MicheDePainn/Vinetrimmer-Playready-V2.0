@echo off
title Vinetrimmer Playready 2.0 Installer

where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing Poetry...
    python -m pip install --upgrade pip
    python -m pip install poetry
) else (
    echo Poetry is already installed, skipping.
)

if exist .venv (
    echo Virtualenv already exists, skipping configuration.
) else (
    echo Configuring Poetry virtualenv...
    poetry config virtualenvs.in-project true
)

if exist .venv\Scripts\python.exe (
    echo Dependencies already installed, skipping.
) else (
    echo Installing dependencies...
    poetry install
)

echo Checking core binaries...
python -c "import os,shutil; bins=['aria2c','ffmpeg','ffprobe','mkvmerge','mp4decrypt','packager','ccextractor','N_m3u8DL-RE']; missing=[b for b in bins if not shutil.which(b) and not os.path.isfile(os.path.join('binaries',b+'.exe')) and not os.path.isfile(os.path.join('binaries',b))]; exit(len(missing))" 2>nul
if %ERRORLEVEL% equ 0 (
    echo Core binaries already present, skipping.
) else (
    echo Downloading core binaries...
    python install_binaries.py
)

echo.
echo Installation complete! You can now use scripts\download.*.bat or run 'poetry run vt dl -h'
pause