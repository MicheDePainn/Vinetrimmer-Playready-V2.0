#!/usr/bin/env bash
echo "========================================================"
echo "                 AppleTVPlus Downloader"
echo "========================================================"
echo ""
read -rp "Enter AppleTV+ URL or ID: " url
echo ""
poetry run vt dl AppleTVPlus "$url"
