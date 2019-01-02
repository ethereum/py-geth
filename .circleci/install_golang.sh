#!/usr/bin/env bash
GO_VERSION=$1
wget "https://dl.google.com/go/go$GO_VERSION.linux-amd64.tar.gz"
sudo tar -zxvf go$GO_VERSION.linux-amd64.tar.gz -C /usr/local/
echo 'export GOROOT=/usr/local/go' >> $BASH_ENV
echo 'export PATH=$PATH:/usr/local/go/bin' >> $BASH_ENV

# Adding the below path to bashrc so that we could put our
# future installed geth executables in below path
echo 'export PATH=$PATH:$HOME/.local/bin' >> $BASH_ENV
