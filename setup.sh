#!/usr/bin/env bash

url=$(curl -s https://api.github.com/repos/ETH-NEXUS/dcc/releases/latest | grep browser_download_url | cut -d '"' -f 4)
curl -s -L -o dcc.tar.gz ${url}

tar xzf dcc.tar.gz

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo cp dist/linux/dcc /usr/bin
elif [[ "$OSTYPE" == "darwin"* ]]; then
    sudo cp dist/mac/dcc ${1:-/usr/bin}
fi

rm -rf dist dcc.tar.gz
