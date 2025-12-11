#!/bin/bash

# Script to download the latest version of Quarto for Ubuntu

set -e

echo "Fetching latest Quarto version..."

# Get the latest release version from GitHub API
LATEST_VERSION=$(curl -s https://api.github.com/repos/quarto-dev/quarto-cli/releases/latest | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Could not fetch the latest version"
    exit 1
fi

echo "Latest Quarto version: $LATEST_VERSION"

# Construct download URL for the Ubuntu/Debian .deb package
DOWNLOAD_URL="https://github.com/quarto-dev/quarto-cli/releases/download/v${LATEST_VERSION}/quarto-${LATEST_VERSION}-linux-amd64.deb"

echo "Downloading from: $DOWNLOAD_URL"

# Download the .deb file
curl -LO "$DOWNLOAD_URL"

if [ -f "quarto-${LATEST_VERSION}-linux-amd64.deb" ]; then
    echo ""
    echo "Download complete: quarto-${LATEST_VERSION}-linux-amd64.deb"
    echo ""
    echo "To install, run:"
    echo "  sudo apt install ./quarto-${LATEST_VERSION}-linux-amd64.deb"
else
    echo "Error: Download failed"
    exit 1
fi
