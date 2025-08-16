# Ubuntu Setup

## Step 1: Install Git and GitHub CLI

    sudo apt update && sudo apt upgrade -y && sudo apt install -y git gh

## Step 2: Authenticate with Git

    gh auth login

## Step 3: Run Setup Script

    wget -O- https://raw.githubusercontent.com/lab1702/setup/refs/heads/main/setup.sh | bash

