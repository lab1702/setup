#!/bin/bash

detect_wsl() {
    if [[ -f /proc/sys/fs/binfmt_misc/WSLInterop ]]; then
        return 0  # WSL2
    fi

    if [[ -n "$WSL_DISTRO_NAME" ]] || [[ -n "$WSLENV" ]]; then
        return 0  # WSL
    fi

    if [[ -f /proc/version ]] && grep -qEi "(Microsoft|WSL)" /proc/version; then
        return 0  # WSL
    fi

    return 1  # Not WSL
}

echo "Updating Ubuntu Packages..."
sudo apt update && \
  sudo apt upgrade -y && \
  sudo apt autoremove -y && \
  sudo apt autoclean -y

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
  r-base \
  r-base-dev \
  python3-venv \
  python3-virtualenv \
  golang \
  rust-all \
  gnucobol \
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

echo "Updating Snaps..."
sudo snap refresh

echo "Installing Snaps..."
sudo snap install astral-uv --classic
sudo snap install helix --classic

if detect_wsl; then
  echo "Running on WSL, skipping some Snaps."
else
  echo "Installing non-WSL Snaps..."
  sudo snap install code --classic
  sudo snap install discord
fi

echo "Adding ${USER} to docker group..."
sudo usermod -aG docker ${USER}

echo "DONE!"
