# Simple Debian / Ubuntu Developer Workstation Setup

**This is focused around C, C++, R, Python, DuckDB, NodeJS, Go, and Rust.**

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Step 3: Configure NPM directory

    mkdir ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    export PATH=~/.npm-global/bin:$PATH

## Step 4: Install Copilot CLI

    npm install -g @github/copilot

## Optional: Setup Git Authentication

Step A:

    git config --global user.name "abc"

Step B:

    git config --global user.email "abc@gmail.com"

Step C:

    gh auth login

Optional Step D:

    gh auth setup-git
