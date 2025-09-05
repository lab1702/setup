#!/bin/bash

detect_ubuntu() {
    if grep -q "ubuntu" /etc/os-release 2>/dev/null; then
        return 0  # Ubuntu
    fi
    return 1  # Not Ubuntu
}

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

echo "**************************"
echo "Updating Linux Packages..."
echo "**************************"
sudo apt update && \
  sudo apt upgrade -y && \
  sudo apt autoremove -y && \
  sudo apt autoclean -y

echo "****************************"
echo "Installing Linux Packages..."
echo "****************************"
sudo apt install -y \
  build-essential \
  gpg \
  git \
  gh \
  cmake \
  unzip \
  jq \
  ripgrep \
  fd-find \
  fzf \
  tree \
  docker.io \
  docker-buildx \
  r-base \
  r-base-dev \
  libopenblas-dev \
  pandoc \
  libxml2-dev \
  libcurl4-openssl-dev \
  libssl-dev \
  libx11-dev \
  libglu1-mesa-dev \
  libftgl-dev \
  libfontconfig1-dev \
  libcairo2-dev \
  libgsl-dev \
  libudunits2-dev \
  libgdal-dev \
  libmpfr-dev \
  libgmp-dev \
  libharfbuzz-dev \
  libfribidi-dev \
  libunwind-dev \
  libarchive-dev \
  libsodium-dev \
  libsecret-1-dev \
  libgit2-dev \
  libmagick++-dev \
  libpoppler-cpp-dev \
  libavfilter-dev \
  libnode-dev \
  unixodbc-dev \
  tdsodbc \
  sqlite3 \
  sqlite3-tools \
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
  htop \
  btop \
  nvtop \
  jnettop

echo "*********************************"
echo "Adding ${USER} to docker group..."
echo "*********************************"
sudo usermod -aG docker ${USER}

if detect_ubuntu; then
  echo "*****************************"
  echo "Installing Ubuntu Packages..."
  echo "*****************************"
  sudo apt install -y \
    docker-compose-v2
else
  echo "*****************************"
  echo "Installing Debian Packages..."
  echo "*****************************"
  sudo apt install -y \
    docker-compose
fi

if detect_wsl; then
  echo "*************************************"
  echo "Configuring Microsoft Edge for WSL..."
  echo "*************************************"
  sudo update-alternatives --install /usr/bin/x-www-browser x-www-browser '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' 200
  sudo update-alternatives --auto x-www-browser
else
  echo "******************************"
  echo "Installing Non-WSL packages..."
  echo "******************************"
  sudo apt install -y \
    fonts-3270 \
    fonts-cascadia-code \
    fonts-hack \
    fonts-jetbrains-mono \
    fonts-recommended \
    gnome-shell-extension-manager

  echo "****************************"
  echo "Installing Microsoft Edge..."
  echo "****************************"
  wget -O /tmp/microsoft-edge.deb https://go.microsoft.com/fwlink?linkid=2149051
  sudo apt-get install -y /tmp/microsoft-edge.deb
  rm /tmp/microsoft-edge.deb

  echo "**********************"
  echo "Installing Warp.Dev..."
  echo "**********************"
  wget -qO- https://releases.warp.dev/linux/keys/warp.asc | gpg --dearmor > /tmp/warpdotdev.gpg
  sudo install -D -o root -g root -m 644 /tmp/warpdotdev.gpg /etc/apt/keyrings/warpdotdev.gpg
  sudo sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/warpdotdev.gpg] https://releases.warp.dev/linux/deb stable main" > /etc/apt/sources.list.d/warpdotdev.list'
  rm /tmp/warpdotdev.gpg
  sudo apt update && sudo apt install warp-terminal
fi

echo "************************"
echo "Installing DuckDB CLI..."
echo "************************"
wget https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
sudo mv duckdb /usr/local/bin/duckdb
rm duckdb_cli-linux-amd64.zip

echo "****************"
echo "Installing UV..."
echo "****************"
curl -fsSL https://astral.sh/uv/install.sh | sh

echo "*****"
echo "DONE!"
echo "*****"
echo
echo "Close the terminal and reopen it for updated path to take effect."
echo
