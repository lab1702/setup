#!/bin/bash

# Script to configure gnome-terminal with dark theme and Gnome colors
# Run this script to apply dark theme settings to your default terminal profile

echo "Configuring gnome-terminal with dark theme and Gnome colors..."

# Get the default profile UUID
PROFILE=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d "'")

# Base path for terminal profile settings
PROFILE_PATH="org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/"

# Set dark theme
echo "Setting dark theme..."
gsettings set $PROFILE_PATH use-theme-colors false
gsettings set $PROFILE_PATH use-theme-transparency false

# Configure dark background and foreground colors
echo "Configuring colors..."
gsettings set $PROFILE_PATH background-color 'rgb(23,20,33)'
gsettings set $PROFILE_PATH foreground-color 'rgb(208,207,204)'

# Set color palette (Gnome dark colors)
gsettings set $PROFILE_PATH palette "['rgb(23,20,33)', 'rgb(192,28,40)', 'rgb(38,162,105)', 'rgb(162,115,76)', 'rgb(18,72,139)', 'rgb(163,71,186)', 'rgb(42,161,179)', 'rgb(208,207,204)', 'rgb(94,92,100)', 'rgb(246,97,81)', 'rgb(51,218,122)', 'rgb(233,173,12)', 'rgb(42,123,222)', 'rgb(192,97,203)', 'rgb(51,199,222)', 'rgb(255,255,255)']"

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

# Configure terminal behavior
echo "Configuring terminal behavior..."
gsettings set $PROFILE_PATH audible-bell false
gsettings set $PROFILE_PATH visible-bell false
gsettings set $PROFILE_PATH scrollback-unlimited false
gsettings set $PROFILE_PATH scrollback-lines 10000

# Set window title
gsettings set $PROFILE_PATH dynamic-title true
gsettings set $PROFILE_PATH title 'Terminal'

# Optional: Set transparency (uncomment if desired)
# gsettings set $PROFILE_PATH use-transparent-background true
# gsettings set $PROFILE_PATH background-transparency-percent 10

echo "Configuration complete! Please restart gnome-terminal or open a new tab to see changes."
echo ""
echo "Profile configured: $PROFILE"
echo "If you want to revert changes, you can reset with:"
echo "gsettings reset-recursively $PROFILE_PATH"
