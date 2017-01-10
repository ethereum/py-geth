#!/bin/bash
#
# Install solc 
#

set -e
set -u

if [ ! -e geth-versions/geth-1.5.5/go-ethereum-1.5.5/build/bin/geth ] ; then
    mkdir -p geth-versions/geth-1.5.5
    cd geth-versions/geth-1.5.5
    wget -O geth.tar.gz "https://github.com/ethereum/go-ethereum/archive/v1.5.5.tar.gz"
    tar -zxvf geth.tar.gz
    cd go-ethereum-1.5.5
    PATH=/usr/lib/go-1.7/bin:$PATH make geth
    echo "Geth installed at $PWD/build/bin/geth"
else
    echo "Geth installed at $PWD/geth-versions/geth-1.5.5/go-ethereum-1.5.5/build/bin/geth"
fi
