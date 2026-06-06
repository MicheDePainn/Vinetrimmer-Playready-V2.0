#!/usr/bin/env bash
echo "========================================================"
echo "                 Hulu Downloader"
echo "========================================================"
echo ""
read -rp "Enter Hulu Movie/Series URL: " url
echo ""
poetry run vt dl Hulu "$url"
