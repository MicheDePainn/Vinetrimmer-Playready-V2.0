@echo off
title Vinetrimmer - ParamountPlus Downloader
echo ========================================================
echo                 ParamountPlus Downloader
echo ========================================================
echo.
set /p url="Enter Paramount+ URL: "
echo.
poetry run vt dl ParamountPlus "%url%"
pause
