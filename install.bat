@echo off
setlocal enabledelayedexpansion
title Vinetrimmer Playready 2.0 Installer

echo ========================================================
echo           Vinetrimmer Playready 2.0 Installer
echo ========================================================
echo.

:: Vérification de la présence de Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Erreur : Python n'est pas installe ou n'est pas ajoute au PATH.
    echo Veuillez installer Python et cocher l'option "Add python.exe to PATH".
    exit /b 1
)

:: Installation de Poetry
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing Poetry...
    python -m pip install --upgrade pip
    python -m pip install poetry
) else (
    echo Poetry is already installed, skipping.
)

:: Configuration du Virtualenv
if exist .venv (
    echo Virtualenv already exists, skipping configuration.
) else (
    echo Configuring Poetry virtualenv...
    poetry config virtualenvs.in-project true
)

:: Installation des dépendances
if exist .venv\Scripts\python.exe (
    echo Dependencies already installed, skipping.
) else (
    echo Installing dependencies...
    :: Note: CFLAGS n'est pas injecté ici car l'environnement MSVC ou MinGW sous Windows 
    :: gère différemment les avertissements de types de pointeurs que GCC/Clang.
    poetry install
)

:: Vérification et téléchargement des binaires
echo Checking core binaries...
python -c "import os, shutil; bins=['aria2c','ffmpeg','ffprobe','mkvmerge','mp4decrypt','packager','ccextractor','N_m3u8DL-RE']; missing=[b for b in bins if not shutil.which(b) and not os.path.isfile(os.path.join('binaries', b)) and not os.path.isfile(os.path.join('binaries', b + '.exe'))]; exit(len(missing))" 2>nul
if %ERRORLEVEL% equ 0 (
    echo Core binaries already present, skipping.
) else (
    echo Downloading core binaries...
    python install_binaries.py
)

echo.
echo Installation complete! You can now run 'poetry run vt dl -h' or use the download scripts.
echo.
echo Quick start:
echo   poetry run vt dl -h
echo   poetry run vt dl --list AMZN B123456789
echo   poetry run vt dl DSNP entity_id
echo   scripts\download.Amazon.bat
echo.
pause