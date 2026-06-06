@echo off
title Vinetrimmer - FranceTV Downloader
echo ========================================================
echo                 FranceTV Downloader
echo ========================================================
echo.
set /p url="Enter France.tv URL: "
echo.
poetry run vt dl FranceTV "%url%"
pause
