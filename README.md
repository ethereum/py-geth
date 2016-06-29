# PyGeth

[![Build Status](https://travis-ci.org/pipermerriam/py-geth.png)](https://travis-ci.org/pipermerriam/py-geth)
[![Documentation Status](https://readthedocs.org/projects/py-geth/badge/?version=latest)](https://readthedocs.org/projects/py-geth/?badge=latest)
[![PyPi version](https://pypip.in/v/py-geth/badge.png)](https://pypi.python.org/pypi/py-geth)
[![PyPi downloads](https://pypip.in/d/py-geth/badge.png)](https://pypi.python.org/pypi/py-geth)
   

Python wrapper around running `geth` as a subprocess


# Dependency

This library requires the `geth` executable to be present.


# Quickstart

Installation

```sh
pip install py-geth
```

To run geth connected to the mainnet


```python
>>> from pygeth.geth import LiveGethProcess
>>> geth = LiveGethProcess()
>>> geth.start()
```

Or a private local chain for testing.  These require you to give them a name.

```python
>>> from pygeth.geth import DevGethProcess
>>> geth = DevGethProcess('testing')
>>> geth.start()
```


Each instance has a few convenient properties.

```python
>>> geth.data_dir
"~/.ethereum"
>>> geth.rpc_port
8545
>>> geth.ipc_path
"~/.ethereum/geth.ipc"
```


For additional information take a look at the source code.
