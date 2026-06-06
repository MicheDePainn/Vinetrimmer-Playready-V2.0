@echo off
title Vinetrimmer - Max Downloader
echo ========================================================
echo                 Max Downloader
echo ========================================================
echo.
set /p url="Enter Max URL: "
echo.
poetry run vt dl Max "%url%"
pause
