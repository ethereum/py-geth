# py-geth

[![Join the conversation on Discord](https://img.shields.io/discord/809793915578089484?color=blue&label=chat&logo=discord&logoColor=white)](https://discord.gg/GHryRvPB84)
[![Tests](https://github.com/ApeWorX/py-geth/actions/workflows/test.yaml/badge.svg)](https://github.com/ApeWorX/py-geth/actions/workflows/test.yaml)
[![PyPI version](https://badge.fury.io/py/py-geth.svg)](https://badge.fury.io/py/py-geth)
[![Python versions](https://img.shields.io/pypi/pyversions/py-geth.svg)](https://pypi.python.org/pypi/py-geth)

Python wrapper around running `geth` as a subprocess

## System Dependency

This library requires the `geth` executable to be present.

> If managing your own bundled version of geth, set the path to the binary using the `GETH_BINARY` environment variable.

## Installation

```bash
python -m pip install py-geth
```

## Quickstart

To run geth connected to the mainnet

```python
>>> from geth import MainnetGethProcess
>>> geth = MainnetGethProcess()
>>> geth.start()
```

Or in dev mode for testing. These require you to give them a name.

```python
>>> from geth import DevGethProcess
>>> geth = DevGethProcess('testing')
>>> geth.start()
```

By default the `DevGethProcess` sets up test chains in the default `datadir`
used by `geth`. If you would like to change the location for these test
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
>>> geth.version
"1.17.8-stable"
```

When testing it can be nice to see the logging output produced by the `geth`
process. `py-geth` provides a mixin class that can be used to log the stdout
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
connections. You can use the following interfaces to query whether these are ready.

```python
>>> geth.wait_for_rpc(timeout=30)  # wait up to 30 seconds for the RPC connection to open
>>> geth.is_rpc_ready
True
>>> geth.wait_for_ipc(timeout=30)  # wait up to 30 seconds for the IPC socket to open
>>> geth.is_ipc_ready
True
```

## Installing specific versions of `geth`

> This feature is experimental, best-effort, and subject to breaking changes.
> Historical tags may become incompatible with current Go toolchains. Prefer
> geth's official downloads or another supported installation method for normal
> use.

Versions of `geth` dating back to v1.14.0 can be installed using `py-geth`.
See [install.py](https://github.com/ApeWorX/py-geth/blob/main/geth/install.py) for
the current list of supported versions.

Installation can be done via the command line:

```bash
$ python -m geth.install v1.17.8
```

Or from python using the `install_geth` function.

```python
>>> from geth import install_geth
>>> install_geth('v1.17.8')
```

The installed binary can be found in the `$HOME/.py-geth` directory, under your
home directory. The `v1.17.8` binary would be located at
`$HOME/.py-geth/geth-v1.17.8/bin/geth`.

The test suite includes a real source-installation test that clones and builds
geth in a pytest temporary directory:

```bash
uv run --group test pytest tests/installation/test_geth_installation.py
```

## About `DevGethProcess`

The `DevGethProcess` will run geth in `--dev` mode and is designed to facilitate testing.
In that regard, it is preconfigured as follows.

- A single account is created, allocated 1 billion ether, and assigned as the coinbase.
- All APIs are enabled on both `rpc` and `ipc` interfaces.
- Networking is configured to not look for or connect to any peers.
- A `networkid` is not set as one can no longer be set along with `--dev`.
- Verbosity is set to `5` (DEBUG)
- The RPC interface *tries* to bind to 8545 but will find an open port if this
  port is not available.
- The DevP2P interface *tries* to bind to 30303 but will find an open port if this
  port is not available.

## Development

Clone the repository:

```shell
$ git clone git@github.com:ApeWorX/py-geth.git
```

Next, run the following from the newly-created `py-geth` directory:

```sh
$ uv sync
```

### Running the tests

You can run the tests with:

```sh
pytest tests
```

## Developer Setup

If you would like to hack on py-geth, please check out the [Snake Charmers
Tactical Manual](https://github.com/ethereum/snake-charmers-tactical-manual)
for information on how we do:

- Testing
- Pull Requests
- Documentation

We use [prek](https://prek.j178.dev) to maintain consistent code style. Once
installed, it will run automatically with every commit. You can also run it manually
with `uv run prek run --all-files`. If you need to make a commit that skips the `prek` checks, you
can do so with `git commit --no-verify`.

### Development Environment Setup

You can set up your dev environment with the `dev` dependency group, which is
installed by default when you run `uv sync`.

```sh
git clone git@github.com:ApeWorX/py-geth.git
cd py-geth
uv sync
uv run prek install
```

### Release setup

Releases are published from GitHub Releases. The release tag is the canonical
version source, `setuptools-scm` derives the package version from that tag, and
the release workflow publishes to PyPI through trusted publishing.

## Adding Support For New Geth Versions

There is an automation script to facilitate adding support for new geth versions: `update_geth.py`

To add support for a geth version, run the following line from the py-geth directory, substituting
the version for the one you wish to add support for. Note that the `v` in the versioning is
optional.

```shell
$ python update_geth.py v1_16_0
```

To introduce support for more than one version, pass in the versions in increasing order,
ending with the latest version.

```shell
$ python update_geth.py v1_16_1 v1_16_2 v1_16_3
```

Always review your changes before committing as something may cause this existing pattern to change at some point.
It is best to compare the git difference with a previous commit that introduced support for a new geth version to make
sure everything looks good.
