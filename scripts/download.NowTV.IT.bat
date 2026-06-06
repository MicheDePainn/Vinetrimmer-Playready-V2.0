@echo off
title Vinetrimmer - NowTV Downloader
echo ========================================================
echo                 NowTV Downloader
echo ========================================================
echo.
set /p url="Enter NowTV.it ID (e.g. R_182580): "
echo.
poetry run vt dl NowTV "%url%"
pause
