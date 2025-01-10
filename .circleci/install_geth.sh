#!/usr/bin/env bash

python --version

# convert underscored `GETH_VERSION` to dotted format
GETH_VERSION=${GETH_VERSION//_/\.}
export GETH_VERSION
echo "Using Geth version: $GETH_VERSION"

export GETH_BASE_INSTALL_PATH=~/repo/install/

if [ -n "$GETH_VERSION" ]; then python -m geth.install "$GETH_VERSION"; fi
if [ -n "$GETH_VERSION" ]; then export GETH_BINARY="$GETH_BASE_INSTALL_PATH/geth-$GETH_VERSION/bin/geth"; fi
if [ -n "$GETH_VERSION" ]; then $GETH_BINARY version; fi

# Modifying the path is tough with tox, hence copying the executable
# to a known directory which is included in $PATH
cp "$GETH_BINARY" "$HOME"/.local/bin
