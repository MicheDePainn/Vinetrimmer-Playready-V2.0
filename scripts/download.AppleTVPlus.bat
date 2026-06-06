@echo off
title Vinetrimmer - AppleTVPlus Downloader
echo ========================================================
echo                 AppleTVPlus Downloader
echo ========================================================
echo.
set /p url="Enter AppleTV+ URL or ID: "
echo.
poetry run vt dl AppleTVPlus "%url%"
pause
