#!/bin/bash

# Ubuntu GNOME Setup Script

# Set background to solid black
gsettings set org.gnome.desktop.background picture-uri ''
gsettings set org.gnome.desktop.background picture-uri-dark ''
gsettings set org.gnome.desktop.background primary-color '#000000'
gsettings set org.gnome.desktop.background color-shading-type 'solid'

# Turn off automatic screen lock
gsettings set org.gnome.desktop.screensaver lock-enabled false

# Turn on location services
gsettings set org.gnome.system.location enabled true

# Use AM/PM time format (12-hour clock)
gsettings set org.gnome.desktop.interface clock-format '12h'

# Show weekday in top bar
gsettings set org.gnome.desktop.interface clock-show-weekday true

# Turn on night light between 6pm and 6am
gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true
gsettings set org.gnome.settings-daemon.plugins.color night-light-schedule-automatic false
gsettings set org.gnome.settings-daemon.plugins.color night-light-schedule-from 18.0
gsettings set org.gnome.settings-daemon.plugins.color night-light-schedule-to 6.0

# Turn off show home folder on desktop
gsettings set org.gnome.shell.extensions.ding show-home false
