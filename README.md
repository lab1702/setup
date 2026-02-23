# Ubuntu Developer Workstation Setup

## Step 1: Install Ansible

    sudo apt update && sudo apt install -y git ansible

## Step 2: Run ansible-pull

    sudo ansible-pull -U https://github.com/lab1702/setup.git

---

## Optional: Setup NPM

    mkdir -p ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc

## Optional: Setup Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

## Optional: Setup grepai

    curl -fsSL https://ollama.com/install.sh | sh

    curl -sSL https://raw.githubusercontent.com/yoanbernabeu/grepai/main/install.sh | sh

## Optional: Setup Git Authentication

Step A:

    git config --global user.name "abc"

Step B:

    git config --global user.email "abc@gmail.com"

Step C:

    gh auth login

Step D:

    gh auth setup-git
