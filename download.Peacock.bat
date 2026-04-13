@echo off
title Vinetrimmer - Peacock Downloader
echo ========================================================
echo                 Peacock Downloader
echo ========================================================
echo.
set /p url="Enter Peacock URL: "
echo.
poetry run vt dl Peacock "%url%"
pause
