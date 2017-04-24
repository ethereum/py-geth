#!/bin/bash
#
# Install solc 
#

set -e
set -u

if [ ! -e geth-versions/geth-$GETH_VERSION/go-ethereum-$GETH_VERSION/build/bin/geth ] ; then
    mkdir -p geth-versions/geth-$GETH_VERSION
    cd geth-versions/geth-$GETH_VERSION
    wget -O geth.tar.gz "https://github.com/ethereum/go-ethereum/archive/v$GETH_VERSION.tar.gz"
    tar -zxvf geth.tar.gz
    cd go-ethereum-$GETH_VERSION
    PATH=/usr/lib/go-1.7/bin:$PATH make geth
    echo "Geth installed at $TRAVIS_BUILD_DIR/geth-versions/geth-$GETH_VERSION/go-ethereum-$GETH_VERSION/build/bin/geth"
else
    echo "Geth found at $TRAVIS_BUILD_DIR/geth-versions/geth-$GETH_VERSION/go-ethereum-$GETH_VERSION/build/bin/geth"
fi
