# Ubuntu Developer Workstation Setup

## Step 1: Install Ansible

    sudo apt update && sudo apt install -y git ansible

## Step 2: Run ansible-pull

    sudo ansible-pull -U https://github.com/lab1702/setup.git

---

## Optional: Setup Claude Code

    curl -fsSL https://claude.ai/install.sh | bash

## Optional: Setup Starship Prompt

    curl -sS https://starship.rs/install.sh | sh

Do this for bash:

    echo 'eval "$(starship init bash)"' >> $HOME/.bashrc

## Optional: Setup Git Authentication

Step A:

    git config --global user.name "abc"

Step B:

    git config --global user.email "abc@gmail.com"

Step C:

    gh auth login

Step D:

    gh auth setup-git
