py-geth v5.0.0-beta.3 (2024-07-11)
----------------------------------

Features
~~~~~~~~

- Add support for geth ``v1.14.6``. (`#224 <https://github.com/ethereum/py-geth/issues/224>`__)
- Add ``tx_pool_lifetime`` flag option (`#225 <https://github.com/ethereum/py-geth/issues/225>`__)
- Add support for geth ``v1.14.7`` (`#227 <https://github.com/ethereum/py-geth/issues/227>`__)


py-geth v5.0.0-beta.2 (2024-06-28)
----------------------------------

Bugfixes
~~~~~~~~

- Add missing fields for genesis data. Change mixhash -> mixHash to more closely match Geth (`#221 <https://github.com/ethereum/py-geth/issues/221>`__)


py-geth v5.0.0-beta.1 (2024-06-19)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Return type of functions in ``accounts.py`` changed from ``bytes`` to ``str`` (`#199 <https://github.com/ethereum/py-geth/issues/199>`__)
- Changed return type of ``get_geth_version_info_string`` from ``bytes`` to ``str`` (`#204 <https://github.com/ethereum/py-geth/issues/204>`__)
- Use a ``pydantic`` model and a ``TypedDict`` to validate and fill default kwargs for ``genesis_data``. Alters the signature of ``write_genesis_file`` to require ``kwargs`` or a ``dict`` for ``genesis_data``. (`#210 <https://github.com/ethereum/py-geth/issues/210>`__)
- Use ``GethKwargsTypedDict`` to typecheck the ``geth_kwargs`` dict when passed as an argument. Breaks signatures of functions ``get_accounts``, ``create_new_account``, and ``ensure_account_exists``, requiring all ``kwargs`` now. (`#213 <https://github.com/ethereum/py-geth/issues/213>`__)


Bugfixes
~~~~~~~~

- Remove duplicates from dev mode account parsing for ``get_accounts()``. (`#219 <https://github.com/ethereum/py-geth/issues/219>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update documentation for ``DevGethProcess`` transition to using ``geth --dev``. (`#200 <https://github.com/ethereum/py-geth/issues/200>`__)


Features
~~~~~~~~

- Add support for newly released geth version ``v1.13.15``. (`#193 <https://github.com/ethereum/py-geth/issues/193>`__)
- Add support for geth ``v1.14.0`` - ``v1.14.3``, with the exception for the missing geth ``v1.14.1`` release. (`#195 <https://github.com/ethereum/py-geth/issues/195>`__)
- Add support for geth versions ``v1.14.4`` and ``v1.14.5``. (`#206 <https://github.com/ethereum/py-geth/issues/206>`__)
- Update all raised ``Exceptions`` to inherit from a ``PyGethException`` (`#212 <https://github.com/ethereum/py-geth/issues/212>`__)


Internal Changes - for py-geth Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Adding basic type hints across the lib (`#196 <https://github.com/ethereum/py-geth/issues/196>`__)
- Use a pydantic model to validate typing of ``geth_kwargs`` when passed as an argument (`#199 <https://github.com/ethereum/py-geth/issues/199>`__)
- Change args for ``construct_popen_command`` from indivdual kwargs to geth_kwargs and validate with GethKwargs model (`#205 <https://github.com/ethereum/py-geth/issues/205>`__)
- Use the latest golang version ``v1.22.4`` when running CircleCI jobs. (`#206 <https://github.com/ethereum/py-geth/issues/206>`__)
- Refactor ``data_dir`` property of ``BaseGethProcess`` and derived classes to fix typing (`#208 <https://github.com/ethereum/py-geth/issues/208>`__)
- Run ``mypy`` locally with all dev deps installed, instead of using the pre-commit ``mirrors-mypy`` hook (`#210 <https://github.com/ethereum/py-geth/issues/210>`__)
- Add ``fill_default_genesis_data`` function to properly fill ``genesis_data`` defaults (`#215 <https://github.com/ethereum/py-geth/issues/215>`__)


Removals
~~~~~~~~

- Remove support for geth < ``v1.13.0``. (`#195 <https://github.com/ethereum/py-geth/issues/195>`__)
- Remove deprecated ``ipc_api`` and ``miner_threads`` geth cli flags (`#202 <https://github.com/ethereum/py-geth/issues/202>`__)
- Removed deprecated ``LiveGethProcess``, use ``MainnetGethProcess`` instead (`#203 <https://github.com/ethereum/py-geth/issues/203>`__)
- Remove handling of ``--ssh`` geth kwarg (`#205 <https://github.com/ethereum/py-geth/issues/205>`__)
- Drop support for geth ``v1.13.x``, keeping only ``v1.14.0`` and above. Also removes all APIs related to mining, DAG, and the ``personal`` namespace. (`#206 <https://github.com/ethereum/py-geth/issues/206>`__)


py-geth v4.4.0 (2024-03-27)
---------------------------

Features
~~~~~~~~

- Add support for geth ``v1.13.12 and v1.13.13`` (`#188 <https://github.com/ethereum/py-geth/issues/188>`__)
- Add support for ``geth v1.13.14`` (`#189 <https://github.com/ethereum/py-geth/issues/189>`__)


Internal Changes - for py-geth Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Merge template updates, noteably add python 3.12 support (`#186 <https://github.com/ethereum/py-geth/issues/186>`__)


py-geth v4.3.0 (2024-02-12)
---------------------------

Features
~~~~~~~~

- Add support for geth ``v1.13.11`` (`#182 <https://github.com/ethereum/py-geth/issues/182>`__)


py-geth v4.2.0 (2024-01-23)
---------------------------

Features
~~~~~~~~

- Add support for geth ``v1.13.10`` (`#179 <https://github.com/ethereum/py-geth/issues/179>`__)


py-geth v4.1.0 (2024-01-10)
---------------------------

Bugfixes
~~~~~~~~

- Fix issue where could not set custom extraData in chain genesis (`#167 <https://github.com/ethereum/py-geth/issues/167>`__)


Features
~~~~~~~~

- Add support for geth ``1.13.5`` (`#165 <https://github.com/ethereum/py-geth/issues/165>`__)
- Allow clique consensus parameters period and epoch in chain genesis (`#169 <https://github.com/ethereum/py-geth/issues/169>`__)
- Add support for geth ``v1.13.6`` and ``v1.13.7`` (`#173 <https://github.com/ethereum/py-geth/issues/173>`__)
- Add support for geth ``v1.13.8`` (`#175 <https://github.com/ethereum/py-geth/issues/175>`__)
- Added support for ``geth v1.13.9`` (`#176 <https://github.com/ethereum/py-geth/issues/176>`__)


Internal Changes - for py-geth Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Change the name of ``master`` branch to ``main`` (`#166 <https://github.com/ethereum/py-geth/issues/166>`__)


py-geth v4.0.0 (2023-10-30)
---------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Drop support for geth ``v1.9`` and ``v1.10`` series. Shanghai was introduced in geth ``v1.11.0`` so this is a good place to draw the line. Drop official support for Python 3.7. (`#160 <https://github.com/ethereum/py-geth/issues/160>`__)


Features
~~~~~~~~

- Add support for geth ``1.12.0`` and ``1.12.1`` (`#151 <https://github.com/ethereum/py-geth/issues/151>`__)
- Add support for geth versions v1.12.2 to v1.13.4 (`#160 <https://github.com/ethereum/py-geth/issues/160>`__)


Internal Changes - for py-geth Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Use golang version ``1.21.3`` for CI builds to ensure compatibility with the latest version. (`#160 <https://github.com/ethereum/py-geth/issues/160>`__)
- Merge template updates, including using pre-commit for linting and drop ``pkg_resources`` for version info (`#162 <https://github.com/ethereum/py-geth/issues/162>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#152 <https://github.com/ethereum/py-geth/issues/152>`__


py-geth v3.13.0 (2023-06-07)
----------------------------

Features
~~~~~~~~

- Allow initializing `BaseGethProcess` with `stdin`, `stdout`, and `stderr` (`#139 <https://github.com/ethereum/py-geth/issues/139>`__)
- Add support for geth `1.11.6` (`#141 <https://github.com/ethereum/py-geth/issues/141>`__)


Internal Changes - for py-geth Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update `tox` and the way it is installed for CircleCI runs (`#141 <https://github.com/ethereum/py-geth/issues/141>`__)
- merge in python project template (`#142 <https://github.com/ethereum/py-geth/issues/142>`__)
- Changed `.format` strings to f-strings, removed other python2 code (`#146 <https://github.com/ethereum/py-geth/issues/146>`__)


Removals
~~~~~~~~

- Remove `miner.thread` default since no longer supported (`#144 <https://github.com/ethereum/py-geth/issues/144>`__)


3.12.0
------

- Add support for geth `1.11.3`, `1.11.4`, and `1.11.5`
- Add `miner_etherbase` to supported geth kwargs

3.11.0
------

- Upgrade circleci golang version to `1.20.1`
- Add support for python `3.11`
- Add support for geth `1.10.26`, `1.11.0`, `1.11.1`, and `1.11.2`
- Fix incorrect comment in `install_geth.sh`
- Add `clique` to `ALL_APIS`
- Add `gcmode` option to Geth process wrapper

3.10.0
------

- Add support for geth `1.10.24`-`1.10.25`
- Patch CVE-2007-4559 - directory traversal vulnerability

3.9.1
-----

- Add support for geth `1.10.18`-`1.10.23`
- Remove support for geth versions `1.9.X`
- Upgrade CI Go version to `1.18.1`
- Some updates to `setup.py`, `tox.ini`, and circleci `config.yml`
- Update supported python versions to reflect what is being tested
- Add python 3.10 support
- Remove dependency on `idna`
- Remove deprecated `setuptools-markdown`
- Updates to `pytest`, `tox`, `setuptools`, `flake8`, and `pluggy` dependencies
- Spelling fix in `create_new_account` docstring

3.8.0
-----

- Add support for geth 1.10.14-1.10.17

3.7.0
-----

- Remove extraneous logging formatting from the LoggingMixin
- Add support for geth 1.10.12-1.10.13

3.6.0
-----

- Add support for geth 1.10.9-1.10.11
- Add support for python 3.9
- Update flake8 requirement to 3.9.2
- Add script to update geth versions
- Set upgrade block numbers in default config
- Allow passing a port by both string and integer to overrides
- Add --preload flag option
- Add --cache flag option
- Add --tx_pool_global_slots flag option
- Add --tx_pool_price_limit flag option
- Handle StopIteration in JoinableQueues when using LoggingMixin
- General code cleanup

3.5.0
-----

- Add support for geth 1.10.7-1.10.8

3.4.0
-----

- Add support for geth 1.10.6

3.3.0
-----

- Add support for geth 1.10.5

3.2.0
-----

- Add support for geth 1.10.4

3.1.0
-----

- Add support for geth 1.10.2-1.10.3

3.0.0
-----

- Add support for geth 1.9.20-1.10.0
- Remove support for geth <= 1.9.14

2.4.0
-----

- Add support for geth 1.9.13-1.9.19

2.3.0
-----

- Add support for geth 1.9.8-1.9.12

2.2.0
-----

- Add support for geth 1.9.x
- Readme bugfix for pypi badges

2.1.0
-----

- remove support for python 2.x
- Geth versions `<1.7` are no longer tested in CI
- Support for geth versions up to `geth==1.8.22`
- Support for python 3.6 and 3.7

1.10.2
------

- Support for testing and installation of `geth==1.7.2`

1.10.1
------

- Support for testing and installation of `geth==1.7.0`

1.10.0
------

- Support and testing against `geth==1.6.1`
- Support and testing against `geth==1.6.2`
- Support and testing against `geth==1.6.3`
- Support and testing against `geth==1.6.4`
- Support and testing against `geth==1.6.5`
- Support and testing against `geth==1.6.6`
- Support and testing against `geth==1.6.7`

1.9.0
-----

- Rename `LiveGethProcess` to `MainnetGethProcess`.  `LiveGethProcess` now raises deprecation warning when instantiated.
- Implement `geth` installation scripts and API
- Expand test suite to cover through `geth==1.6.6`

1.8.0
-----

- Bugfix for `--ipcapi` flag removal in geth 1.6.x

1.7.1
-----

- Bugfix for `ensure_path_exists` utility function.

1.7.0
-----

- Change to use `compat` instead of `async` since async is a keyword
- Change env variable for gevent threading to be `GETH_THREADING_BACKEND`

1.6.0
-----

- Remove hard dependency on gevent.
- Expand testing against 1.5.5 and 1.5.6

1.5.0
-----

- Deprecate the `--testnet` based chain.
- TestnetGethProcess now is an alias for whatever the current primary testnet is
- RopstenGethProcess now represents the current ropsten test network
- travis-ci geth version pinning.

1.4.1
-----

- Add `rpc_cors_domain` to supported arguments for running geth instances.

1.4.0
-----

- Add `shh` flag to wrapper to allow enabling of whisper in geth processes.

1.3.0
-----

- Bugfix for python3 when no contracts are found.
- Allow genesis configuration through constructor of GethProcess classes.

1.2.0
-----

- Add gevent monkeypatch for socket when using requests and urllib.

1.1.0
-----

- Fix websocket addition

1.0.0
-----

- Add Websocket interface to default list of interfaces that are presented by
  geth.

0.9.0
-----

- Fix broken LiveGethProcess and TestnetGethProcess classes.
- Let DevGethProcesses use a local geth.ipc if the path is short enough.

0.8.0
-----

- Add `homesteadBlock`, `daoForkBlock`, and `doaForkSupport` to the genesis
  config that is written for test chains.

0.7.0
-----

- Rename python module from `pygeth` to `geth`

0.6.0
-----

- Add `is_rpc_ready` and `wait_for_rpc` api.
- Add `is_ipc_ready` and `wait_for_ipc` api.
- Add `is_dag_generated` and `wait_for_dag` api.
- Refactor `LoggingMixin` core logic into base `InterceptedStreamsMixin`


0.5.0
-----

- Fix deprecated usage of `--genesis`


0.4.0
-----

- Fix broken loggin mixin (again)


0.3.0
-----

- Fix broken loggin mixin.


0.2.0
-----

- Add logging mixins


0.1.0
-----

- Initial Release
