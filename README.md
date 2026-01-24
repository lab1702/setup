# Simple Debian / Ubuntu Developer Workstation Setup

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Optional: Configure GNOME

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/ubuntu-gnome-setup.sh | bash

## Optional: Install Niri

    sudo add-apt-repository ppa:avengemedia/danklinux
    sudo add-apt-repository ppa:avengemedia/dms
    sudo apt install niri dms

## Optional: Download Quarto

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/download-quarto.sh | bash

## Optional: Setup Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

### Add AgentOS for Claude

    cd ~ && git clone https://github.com/buildermethods/agent-os.git && rm -rf ~/agent-os/.git

## Optional: Setup OpenCode

    curl -fsSL https://opencode.ai/install | bash

## Optional: Setup Git Authentication

Step A:

    git config --global user.name "abc"

Step B:

    git config --global user.email "abc@gmail.com"

Step C:

    gh auth login

Step D:

    gh auth setup-git

## Optional: Find battle.net launcher install paths

    BPN=$(find ~/ -name "Battle.net Launcher.exe" 2>/dev/null | head -n 1); printf "\nTARGET:\n\"%s\"\n\nSTART IN:\n\"%s\"\n\n" "$BPN" "$(dirname "$BPN")"

## Optional: Setup VHS

    go install github.com/charmbracelet/vhs@latest
