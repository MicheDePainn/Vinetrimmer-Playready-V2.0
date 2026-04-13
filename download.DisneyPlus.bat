@echo off
title Vinetrimmer - DisneyPlus Downloader
echo ========================================================
echo                 DisneyPlus Downloader
echo ========================================================
echo.
set /p url="Enter Disney+ URL or Entity ID: "
echo.
poetry run vt dl DisneyPlus "%url%"
pause
