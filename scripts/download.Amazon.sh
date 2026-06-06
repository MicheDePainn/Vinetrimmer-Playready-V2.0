#!/usr/bin/env bash
echo "========================================================"
echo "                 Amazon Downloader"
echo "========================================================"
echo ""
read -rp "Enter Amazon URL or ASIN: " url
echo ""
poetry run vt dl Amazon "$url"
