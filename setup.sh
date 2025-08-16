#!/bin/bash

echo "Updating Ubuntu Packages..."
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y && sudo apt autoclean -y

echo "Installing Ubuntu Packages..."
sudo apt install -y \
  build-essential \
  cmake \
  curl \
  jq \
  ripgrep \
  fd-find \
  fzf \
  tree \
  docker.io \
  docker-buildx \
  docker-compose-v2 \
  python3-venv \
  python3-virtualenv \
  vim \
  cpufetch \
  figlet \
  dos2unix \
  btop \
  nvtop

echo "Installing DuckDB..."
wget https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
sudo mv duckdb /usr/local/bin/duckdb
rm duckdb_cli-linux-amd64.zip
