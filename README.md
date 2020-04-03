# PyGeth

[![Build Status](https://travis-ci.org/pipermerriam/py-geth.png)](https://travis-ci.org/pipermerriam/py-geth)
[![Documentation Status](https://readthedocs.org/projects/py-geth/badge/?version=latest)](https://readthedocs.org/projects/py-geth/?badge=latest)
[![PyPi version](https://img.shields.io/pypi/v/py-geth.svg)](https://pypi.python.org/pypi/py-geth)


Python wrapper around running `geth` as a subprocess


## System Dependency

This library requires the `geth` executable to be present.


## Installation

Installation

```bash
pip install py-geth
```

## Quickstart


To run geth connected to the mainnet


```python
>>> from geth import LiveGethProcess
>>> geth = LiveGethProcess()
>>> geth.start()
```

Or a private local chain for testing.  These require you to give them a name.

```python
>>> from geth import DevGethProcess
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
>>> from geth import LoggingMixin, DevGethProcess
>>> class MyGeth(LoggingMixin, DevGethProcess):
...     pass
>>> geth = MyGeth()
>>> geth.start()
```

All logs will be written to logfiles in `./logs/` in the current directory.

The underlying `geth` process can take additional time to open the RPC or IPC
connections, as well as to start mining if it needs to generate the DAG.  You
can use the following interfaces to query whether these are ready.

```python
>>> geth.is_rpc_ready
True
>>> geth.wait_for_rpc(timeout=30)  # wait up to 30 seconds for the RPC connection to open
>>> geth.is_ipc_ready
True
>>> geth.wait_for_ipc(timeout=30)  # wait up to 30 seconds for the IPC socket to open
>>> geth.is_dag_generated
True
>>> geth.is_mining
True
>>> geth.wait_for_dag(timeout=600)  # wait up to 10 minutes for the DAG to generate.
```

> The DAG functionality currently only applies to the DAG for epoch 0.


# Installing specific versions of `geth`

> This feature is experimental and subject to breaking changes.

Any of the following versions of `geth` can be installed using `py-geth` on the
listed platforms.

* `v1.5.6` (linux/osx)
* `v1.5.7` (linux/osx)
* `v1.5.8` (linux/osx)
* `v1.5.9` (linux/osx)
* `v1.6.0` (linux/osx)
* `v1.6.1` (linux/osx)
* `v1.6.2` (linux/osx)
* `v1.6.3` (linux/osx)
* `v1.6.4` (linux/osx)
* `v1.6.5` (linux/osx)
* `v1.6.6` (linux/osx)
* `v1.6.7` (linux/osx)
* `v1.7.0` (linux/osx)
* `v1.7.2` (linux/osx)
* `v1.8.1` (linux/osx)

Installation can be done via the command line:

```bash
$ python -m geth.install v0.4.12
```

Or from python using the `install_geth` function.

```python
>>> from geth import install_geth
>>> install_geth('v1.7.0')
```

The installed binary can be found in the `$HOME/.py-geth` directory, under your
home directory.  The `v1.7.0` binary would be located at
`$HOME/.py-geth/geth-v1.7.0/bin/geth`.


# About `DevGethProcess`

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


## Development

Clone the repository and then run:

```sh
pip install -e .[dev]
```


### Running the tests

You can run the tests with:

```sh
pytest tests
```

Or you can install `tox` to run the full test suite.


### Releasing

Pandoc is required for transforming the markdown README to the proper format to
render correctly on pypi.

For Debian-like systems:

```
apt install pandoc
```

Or on OSX:

```sh
brew install pandoc
```

To release a new version:

```sh
make release bump=$$VERSION_PART_TO_BUMP$$
```

#### How to bumpversion

The version format for this repo is `{major}.{minor}.{patch}` for stable, and
`{major}.{minor}.{patch}-{stage}.{devnum}` for unstable (`stage` can be alpha or beta).

To issue the next version in line, specify which part to bump,
like `make release bump=minor` or `make release bump=devnum`.

If you are in a beta version, `make release bump=stage` will switch to a stable.

To issue an unstable version when the current version is stable, specify the
new version explicitly, like `make release bump="--new-version 4.0.0-alpha.1 devnum"`
