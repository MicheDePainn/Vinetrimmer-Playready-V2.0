@echo off
title Vinetrimmer - Hulu Downloader
echo ========================================================
echo                 Hulu Downloader
echo ========================================================
echo.
set /p url="Enter Hulu Movie/Series URL: "
echo.
poetry run vt dl Hulu "%url%"
pause
