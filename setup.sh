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
  octave \
  r-base \
  r-base-dev \
  libopenblas-dev \
  tidy \
  pandoc \
  texlive-full \
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
  libabsl-dev \
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
  jnettop \
  ffmpeg \
  ttyd

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
  echo "*****************************"
  echo "WSL Specific items go here..."
  echo "*****************************"
  sudo apt install -y \
    wslu
else
  echo "*********************************"
  echo "Non-WSL Specific items go here..."
  echo "*********************************"
  wget -O /tmp/microsoft-edge.deb https://go.microsoft.com/fwlink?linkid=2149051
  sudo apt-get install -y /tmp/microsoft-edge.deb
  rm /tmp/microsoft-edge.deb

  sudo apt install -y \
    fonts-firacode
fi

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
echo
echo "Close the terminal and reopen it for updated path to take effect."
echo
