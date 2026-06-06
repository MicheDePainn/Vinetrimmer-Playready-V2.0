#!/usr/bin/env bash
echo "========================================================"
echo "                 CanalPlus Downloader"
echo "========================================================"
echo ""
read -rp "Enter Canal+ URL: " url
echo ""
poetry run vt dl CanalPlus "$url"
