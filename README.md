# Ubuntu Setup

*My setup emphasizes simplicity and minimalism. There is nothing that affects themes and looks here.*

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl git gh

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Step 3: Install Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

## Step 4: Install OpenCode

    curl -fsSL https://opencode.ai/install | bash

## Step 5: Install NodeJS NVM

    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/refs/heads/master/install.sh | bash

## Step 6: Install Microsoft Edge

    wget -O microsoft-edge.deb https://go.microsoft.com/fwlink?linkid=2149051
    sudo apt-get install -y ./microsoft-edge.deb
    rm microsoft-edge.deb
