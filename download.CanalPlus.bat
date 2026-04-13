@echo off
title Vinetrimmer - CanalPlus Downloader
echo ========================================================
echo                 CanalPlus Downloader
echo ========================================================
echo.
set /p url="Enter Canal+ URL: "
echo.
poetry run vt dl CanalPlus "%url%"
pause
