#!/bin/bash

detect_snapd() {
    if command -v snap >/dev/null 2>&1; then
        return 0  # snapd is available
    fi
    return 1  # snapd not available
}

detect_debian() {
    if grep -q "debian" /etc/os-release 2>/dev/null; then
        return 0  # Debian
    fi
    return 1  # Not Debian
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

if ! detect_snapd; then
    echo "*******************"
    echo "Installing snapd..."
    echo "*******************"
    if detect_debian; then
        sudo apt install -y snapd
        # sudo systemctl enable --now snapd.socket
        export PATH="$PATH:/snap/bin"
    else
        echo "Please install snapd manually for your distribution"
    fi
fi

echo "*****************"
echo "Updating Snaps..."
echo "*****************"
sudo snap refresh

echo "****************************"
echo "Installing Linux Packages..."
echo "****************************"
sudo apt install -y \
  unzip \
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
  unixodbc-dev \
  tdsodbc \
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

if detect_debian; then
  echo "*****************************"
  echo "Installing Debian Packages..."
  echo "*****************************"
  sudo apt install -y \
    docker-compose \
    libnode-dev
else
  echo "*****************************"
  echo "Installing Ubuntu Packages..."
  echo "*****************************"
  sudo apt install -y \
    docker-compose-v2 \
    libv8-dev
fi

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
