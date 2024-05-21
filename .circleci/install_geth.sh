#!/usr/bin/env bash

python --version
echo $GETH_VERSION
export GETH_BASE_INSTALL_PATH=~/repo/install/
mkdir -p $HOME/.ethash
if [ -n "$GETH_VERSION" ]; then python -m geth.install $GETH_VERSION; fi
if [ -n "$GETH_VERSION" ]; then export GETH_BINARY="$GETH_BASE_INSTALL_PATH/geth-$GETH_VERSION/bin/geth"; fi
if [ -n "$GETH_VERSION" ]; then $GETH_BINARY version; fi

# Modifying the path is tough with tox, hence copying the executable
# to a known directory which is included in $PATH
cp $GETH_BINARY $HOME/.local/bin
