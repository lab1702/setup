# Simple Debian / Ubuntu Developer Workstation Setup

**This is focused around C, C++, R, Python, DuckDB, NodeJS, Go and Rust using Claude Code AI Coding Agent.**

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Step 3: Run Update Script
This will install updates and install/update the DuckDB CLI binary.

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/update.sh | bash

## Optional: Setup Git Authentication

Step A:

    git config --global user.name "name"

Step B:

    git config --global user.email "email"

Step C:

    gh auth login

Step D:

    gh auth setup-git
