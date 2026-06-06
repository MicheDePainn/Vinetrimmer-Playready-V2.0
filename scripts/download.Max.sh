#!/usr/bin/env bash
echo "========================================================"
echo "                 Max Downloader"
echo "========================================================"
echo ""
read -rp "Enter Max URL: " url
echo ""
poetry run vt dl Max "$url"
