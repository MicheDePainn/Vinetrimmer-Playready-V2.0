#!/usr/bin/env bash
echo "========================================================"
echo "                 TimVision Downloader"
echo "========================================================"
echo ""
read -rp "Enter TimVision URL: " url
echo ""
poetry run vt dl TimVision "$url"
