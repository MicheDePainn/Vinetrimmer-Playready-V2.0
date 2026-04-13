@echo off
title Vinetrimmer Playready 2.0 Installer

echo Installing Poetry...
python -m pip install --upgrade pip
python -m pip install poetry

echo Configuring Poetry virtualenv...
poetry config virtualenvs.in-project true

echo Installing dependencies...
poetry install

echo Downloading core binaries...
python install_binaries.py

echo.
echo Installation complete! You can now use the download.*.bat scripts or run 'poetry run vt dl -h'
pause