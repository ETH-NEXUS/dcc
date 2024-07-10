#!/usr/bin/env bash

DIR=$(mktemp -d)
cd ${DIR}

url=$(curl -s https://api.github.com/repos/ETH-NEXUS/dcc/releases/latest | grep browser_download_url | cut -d '"' -f 4)
echo "Downloading latest version of dcc from ${url}..."
curl -s -L -o dcc.tar.gz ${url}

echo "Extracting package..."
tar xzf dcc.tar.gz

target=${1:-~/.local/bin}
mkdir -p ${target}
echo "Installing to ${target}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp dist/linux/dcc ${target}
elif [[ "$OSTYPE" == "darwin"* ]]; then
    cp -r dist/mac/dcc_mac ${target}
    rm -f ${target}/dcc
    ln -sf ${target}/dcc_mac/dcc_mac ${target}/dcc
fi

echo "Cleaning up..."
rm -rf ${DIR}

echo "DONE."
