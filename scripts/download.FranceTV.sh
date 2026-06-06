#!/usr/bin/env bash
echo "========================================================"
echo "                 FranceTV Downloader"
echo "========================================================"
echo ""
read -rp "Enter France.tv URL: " url
echo ""
poetry run vt dl FranceTV "$url"
