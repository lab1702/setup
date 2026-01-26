# Simple Ubuntu Developer Workstation Setup

## Step 1: Install Ansible

    sudo apt update && sudo apt install -y ansible

## Step 2: Run ansible-pull

    sudo ansible-pull -U https://github.com/lab1702/setup.git

Or with verbose output:

    sudo ansible-pull -U https://github.com/lab1702/setup.git -v

---

## Optional: Setup Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

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
