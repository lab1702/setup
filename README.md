# Simple Ubuntu Developer Workstation Setup

**This is focused around C, C++, R, Python, DuckDB, NodeJS, Go and Rust using Claude Code AI Coding Agent.**

*My setup emphasizes simplicity and minimalism. There is nothing that affects themes and looks here.*

## Step 1: Install Basics

    sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget git

## Step 2: Run Setup Script

    curl -fsSL https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

## Step 3: Install Microsoft Edge ***(NOT FOR WSL)***

    wget -O /tmp/microsoft-edge.deb https://go.microsoft.com/fwlink?linkid=2149051
    sudo apt-get install -y /tmp/microsoft-edge.deb
    rm /tmp/microsoft-edge.deb

## Step 4: Configure Global NPM Directory

    mkdir ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    export PATH=~/.npm-global/bin:$PATH

## Step 5: Install Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

And add it to path:

    echo 'export PATH="~/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="~/.local/bin:$PATH"

## Step 6: Install MCPs

### Playwright

    claude mcp add playwright npx @playwright/mcp@latest

### Context7

    claude mcp add --transport sse context7 https://mcp.context7.com/sse
