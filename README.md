# Ubuntu Developer Workstation Setup

## Step 0: Setup up fingerprint Authentication
_If applicable do this after enrolling your fingerprint_

    sudo pam-auth-update

## Step 1: Enable AMD64v3 CPU Optimizations (AMD64 only)

Skip this step on ARM64 workstations. On AMD64, confirm that the CPU supports
the x86-64-v3 feature level before enabling this setting.

    echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
    sudo apt update && sudo apt upgrade

## Step 2: Install Ansible

    sudo apt update && sudo apt upgrade -y &&  sudo apt install -y git ansible

## Step 3: Run ansible-pull

    sudo ansible-pull -U https://github.com/lab1702/setup.git

---

## Optional: Setup NPM

    mkdir -p ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc

## Optional: Setup Claude Code CLI

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
    git config --global init.defaultBranch main
