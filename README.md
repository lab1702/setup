# Ubuntu & Debian Setup

## Step 1: Install Git and GitHub CLI

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl git gh

## Step 2: Authenticate with Git

    gh auth login

## Step 3: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Step 4: Install Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

