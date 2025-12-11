# Simple Debian / Ubuntu Developer Workstation Setup

**This is focused around C, C++, R, Python, DuckDB, NodeJS, Go, and Rust.**

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Optional: Download Quarto

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/download-quarto.sh | bash

## Optional: Configure NPM directory

    mkdir ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    export PATH=~/.npm-global/bin:$PATH

## Optional: Setup Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

## Optional: Setup OpenCode

    curl -fsSL https://opencode.ai/install | bash

## Optional: Setup Git Authentication

Step A:

    git config --global user.name "abc"

Step B:

    git config --global user.email "abc@gmail.com"

Step C:

    gh auth login
