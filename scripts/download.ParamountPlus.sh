#!/usr/bin/env bash
echo "========================================================"
echo "                 ParamountPlus Downloader"
echo "========================================================"
echo ""
read -rp "Enter Paramount+ URL: " url
echo ""
poetry run vt dl ParamountPlus "$url"
