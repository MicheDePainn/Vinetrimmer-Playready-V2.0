#!/usr/bin/env bash
echo "========================================================"
echo "                 DisneyPlus Downloader"
echo "========================================================"
echo ""
read -rp "Enter Disney+ URL or Entity ID: " url
echo ""
poetry run vt dl DisneyPlus "$url"
