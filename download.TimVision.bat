@echo off
title Vinetrimmer - TimVision Downloader
echo ========================================================
echo                 TimVision Downloader
echo ========================================================
echo.
set /p url="Enter TimVision URL: "
echo.
poetry run vt dl TimVision "%url%"
pause
