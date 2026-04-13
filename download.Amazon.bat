@echo off
title Vinetrimmer - Amazon Downloader
echo ========================================================
echo                 Amazon Downloader
echo ========================================================
echo.
set /p url="Enter Amazon URL or ASIN: "
echo.
poetry run vt dl Amazon "%url%"
pause
