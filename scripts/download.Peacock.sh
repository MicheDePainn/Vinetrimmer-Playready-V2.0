#!/usr/bin/env bash
echo "========================================================"
echo "                 Peacock Downloader"
echo "========================================================"
echo ""
read -rp "Enter Peacock URL: " url
echo ""
poetry run vt dl Peacock "$url"
