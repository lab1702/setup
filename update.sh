#!/bin/bash

echo "**************************"
echo "Updating Linux Packages..."
echo "**************************"
sudo apt update && \
  sudo apt upgrade -y && \
  sudo apt autoremove -y && \
  sudo apt autoclean -y

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
