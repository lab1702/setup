# Simple Debian / Ubuntu Developer Workstation Setup

**This is focused around C, C++, R, Python, DuckDB, NodeJS, Go and Rust using Claude Code AI Coding Agent.**

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Optional: Configure Global NPM Directory

    mkdir ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    export PATH=~/.npm-global/bin:$PATH

## Optional: Install Playwright MCP

    claude mcp add playwright npx @playwright/mcp@latest

## Optional: Setup Git Authentication

Step A:

    gh auth login

Step B:

    gh auth setup-git

Step C:

    git config --global user.name "name"

Step D:

    git config --global user.email "email"

## Optional: Set Gnome Terminal Dark Theme

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/gterm_theme.sh | bash

