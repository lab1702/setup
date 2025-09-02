#!/bin/bash

# Script to configure gnome-terminal with dark theme and Gnome colors
# Run this script to apply dark theme settings to your default terminal profile

echo "Configuring gnome-terminal with dark theme and Gnome colors..."

# Get the default profile UUID
PROFILE=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d "'")

# Base path for terminal profile settings
PROFILE_PATH="org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/"

# First reset
echo "Resetting all settings..."
gsettings reset-recursively $PROFILE_PATH

# Set dark theme
echo "Setting dark theme..."
gsettings set $PROFILE_PATH use-theme-colors false
gsettings set $PROFILE_PATH use-theme-transparency false

# Configure dark background and foreground colors
# echo "Configuring colors..."
gsettings set $PROFILE_PATH background-color 'rgb(23,20,33)'
gsettings set $PROFILE_PATH foreground-color 'rgb(208,207,204)'

# Enable custom colors
gsettings set $PROFILE_PATH use-system-font false
gsettings set $PROFILE_PATH font 'Monospace 14'

# Configure cursor and highlight colors
gsettings set $PROFILE_PATH cursor-colors-set true
gsettings set $PROFILE_PATH cursor-background-color 'rgb(208,207,204)'
gsettings set $PROFILE_PATH cursor-foreground-color 'rgb(23,20,33)'

gsettings set $PROFILE_PATH highlight-colors-set true
gsettings set $PROFILE_PATH highlight-background-color 'rgb(18,72,139)'
gsettings set $PROFILE_PATH highlight-foreground-color 'rgb(255,255,255)'

# Set bold color
gsettings set $PROFILE_PATH bold-color 'rgb(255,255,255)'
gsettings set $PROFILE_PATH bold-color-same-as-fg false

echo "Configuration complete! Please restart gnome-terminal or open a new tab to see changes."
echo ""
echo "Profile configured: $PROFILE"
echo "If you want to revert changes, you can reset with:"
echo "gsettings reset-recursively $PROFILE_PATH"
