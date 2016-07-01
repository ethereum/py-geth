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
>>> from pygeth import LiveGethProcess
>>> geth = LiveGethProcess()
>>> geth.start()
```

Or a private local chain for testing.  These require you to give them a name.

```python
>>> from pygeth import DevGethProcess
>>> geth = DevGethProcess('testing')
>>> geth.start()
```

By default the `DevGethProcess` sets up test chains in the default `datadir`
used by `geth`.  If you would like to change the location for these test
chains, you can specify an alternative `base_dir`.

```python
>>> geth = DevGethProcess('testing', '/tmp/some-other-base-dir/')
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
>>> geth.accounts
['0xd3cda913deb6f67967b99d67acdfa1712c293601']
>>> geth.is_alive
False
>>> geth.is_running
False
>>> geth.is_stopped
False
>>> geth.start()
>>> geth.is_alive
True  # indicates that the subprocess hasn't exited
>>> geth.is_running
True  # indicates that `start()` has been called (but `stop()` hasn't)
>>> geth.is_stopped
False
>>> geth.stop()
>>> geth.is_alive
False
>>> geth.is_running
False
>>> geth.is_stopped
True
```

When testing it can be nice to see the logging output produced by the `geth`
process.  `py-geth` provides a mixin class that can be used to log the stdout
and stderr output to a logfile.

```python
>>> from pygeth import LoggingMixin, DevGethProcess
>>> class MyGeth(LoggingMixin, DevGethProcess):
...     pass
>>> geth = MyGeth()
>>> geth.start()
```

All logs will be written to logfiles in `./logs/` in the current directory.


# Aboutn `DevGethProcess`

The `DevGethProcess` is designed to facilitate testing.  In that regard, it is
preconfigured as follows.

* A single account is created and allocated 1 billion ether.
* All APIs are enabled on both `rpc` and `ipc` interfaces.
* Account 0 is unlocked
* Networking is configured to not look for or connect to any peers.
* The `networkid` of `1234` is used.
* Verbosity is set to `5` (DEBUG)
* Mining is enabled with a single thread.
* The RPC interface *tries* to bind to 8545 but will find an open port if this
  port is not available.
* The DevP2P interface *tries* to bind to 30303 but will find an open port if this
  port is not available.


# Gotchas

If you are running with `mining` enabled (which is default for `DevGethProcess`
then you will likely need to generate the `DAG` manually.  If you do not, then
it will auto-generate the first time you run the process and this takes a
while.

To generate it manually:

```sh
$ geth makedag 0 ~/.ethash
```

This is especially important in CI environments like Travis-CI where your
process will likely timeout during generation.
