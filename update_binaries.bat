@echo off
setlocal

:: This script runs the update_binaries.py python script to update the binaries.
:: Usage: update_binaries.bat <URL_or_path_to_zip>

if "%~1"=="" (
    echo Usage: %~nx0 ^<URL_or_path_to_zip^>
    echo Please provide a URL or a local path to the zip file containing the new binaries.
    exit /b 1
)

python "%~dp0scripts\update_binaries.py" "%~1"

endlocal
