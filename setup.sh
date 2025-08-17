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

echo "***************************"
echo "Updating Ubuntu Packages..."
echo "***************************"
sudo apt update && \
  sudo apt upgrade -y && \
  sudo apt autoremove -y && \
  sudo apt autoclean -y

echo "*****************"
echo "Updating Snaps..."
echo "*****************"
sudo snap refresh

echo "*****************************"
echo "Installing Ubuntu Packages..."
echo "*****************************"
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
  nodejs \
  npm \
  vim \
  cpufetch \
  figlet \
  dos2unix \
  btop \
  nvtop

echo "*******************"
echo "Installing Snaps..."
echo "*******************"
sudo snap install astral-uv --classic

if detect_wsl; then
  echo "*************************************"
  echo "Configuring Microsoft Edge for WSL..."
  echo "*************************************"
  sudo update-alternatives --install /usr/bin/x-www-browser x-www-browser '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' 200
  sudo update-alternatives --auto x-www-browser
else
  echo "***************************"
  echo "Installing non-WSL Snaps..."
  echo "***************************"
  sudo snap install code --classic
  sudo snap install discord
fi

echo "*********************************"
echo "Adding ${USER} to docker group..."
echo "*********************************"
sudo usermod -aG docker ${USER}

echo "************************"
echo "Installing DuckDB CLI..."
echo "************************"
wget https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
sudo mv duckdb /usr/local/bin/duckdb
rm duckdb_cli-linux-amd64.zip

echo "*****"
echo "DONE!"
echo "*****"
