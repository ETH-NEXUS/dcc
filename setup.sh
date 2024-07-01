#!/usr/bin/env bash

url=$(curl -s https://api.github.com/repos/ETH-NEXUS/dcc/releases/latest | grep browser_download_url | cut -d '"' -f 4)
echo "Downloading latest version of dcc from ${url}..."
curl -s -L -o dcc.tar.gz ${url}

echo "Extracting package..."
tar xzf dcc.tar.gz

target=${1:-~/.local/bin}
echo "Installing to ${target}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo cp dist/linux/dcc ${target}
elif [[ "$OSTYPE" == "darwin"* ]]; then
    sudo cp dist/mac/dcc ${target}
fi

echo "Cleaning up..."
rm -rf dist dcc.tar.gz

echo "DONE."
