#!/usr/bin/env bash
echo "========================================================"
echo "                 NowTV Downloader"
echo "========================================================"
echo ""
read -rp "Enter NowTV.it ID (e.g. R_182580): " url
echo ""
poetry run vt dl NowTV "$url"
