from __future__ import (
    annotations,
)

from abc import (
    ABC,
    abstractmethod,
)
import copy
import json
import logging
import os
import subprocess
import time
from types import (
    TracebackType,
)
from typing import (
    cast,
)
from urllib.error import (
    URLError,
)
from urllib.request import (
    urlopen,
)

import semantic_version

from geth import (
    get_geth_version,
)
from geth.accounts import (
    ensure_account_exists,
    get_accounts,
)
from geth.chain import (
    get_chain_data_dir,
    get_default_base_dir,
    get_genesis_file_path,
    get_live_data_dir,
    get_sepolia_data_dir,
    initialize_chain,
    is_live_chain,
    is_sepolia_chain,
)
from geth.exceptions import (
    PyGethNotImplementedError,
    PyGethValueError,
)
from geth.types import (
    GethKwargsTypedDict,
    IO_Any,
)
from geth.utils.networking import (
    get_ipc_socket,
)
from geth.utils.proc import (
    kill_proc,
)
from geth.utils.timeout import (
    Timeout,
)
from geth.utils.validation import (
    GenesisDataTypedDict,
    validate_genesis_data,
    validate_geth_kwargs,
)
from geth.wrapper import (
    construct_popen_command,
    construct_test_chain_kwargs,
)

logger = logging.getLogger(__name__)
with open(os.path.join(os.path.dirname(__file__), "genesis.json")) as genesis_file:
    GENESIS_JSON = json.load(genesis_file)


class BaseGethProcess(ABC):
    _proc = None

    def __init__(
        self,
        geth_kwargs: GethKwargsTypedDict,
        stdin: IO_Any = subprocess.PIPE,
        stdout: IO_Any = subprocess.PIPE,
        stderr: IO_Any = subprocess.PIPE,
    ):
        validate_geth_kwargs(geth_kwargs)
        self.geth_kwargs = geth_kwargs
        self.command = construct_popen_command(**geth_kwargs)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    is_running = False

    def start(self) -> None:
        if self.is_running:
            raise PyGethValueError("Already running")
        self.is_running = True

        logger.info(f"Launching geth: {' '.join(self.command)}")
        self.proc = subprocess.Popen(
            self.command,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr,
        )

    def __enter__(self) -> BaseGethProcess:
        self.start()
        return self

    def stop(self) -> None:
        if not self.is_running:
            raise PyGethValueError("Not running")

        if self.proc.poll() is None:
            kill_proc(self.proc)

        self.is_running = False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.stop()

    @property
    @abstractmethod
    def data_dir(self) -> str:
        raise PyGethNotImplementedError("Must be implemented by subclasses.")

    @property
    def is_alive(self) -> bool:
        return self.is_running and self.proc.poll() is None

    @property
    def is_stopped(self) -> bool:
        return self.proc is not None and self.proc.poll() is not None

    @property
    def accounts(self) -> tuple[str, ...]:
        return get_accounts(**self.geth_kwargs)

    @property
    def rpc_enabled(self) -> bool:
        _rpc_enabled = self.geth_kwargs.get("rpc_enabled", False)
        return cast(bool, _rpc_enabled)

    @property
    def rpc_host(self) -> str:
        _rpc_host = self.geth_kwargs.get("rpc_host", "127.0.0.1")
        return cast(str, _rpc_host)

    @property
    def rpc_port(self) -> str:
        _rpc_port = self.geth_kwargs.get("rpc_port", "8545")
        return cast(str, _rpc_port)

    @property
    def is_rpc_ready(self) -> bool:
        try:
            urlopen(f"http://{self.rpc_host}:{self.rpc_port}")
        except URLError:
            return False
        else:
            return True

    def wait_for_rpc(self, timeout: int = 0) -> None:
        if not self.rpc_enabled:
            raise PyGethValueError("RPC interface is not enabled")

        with Timeout(timeout) as _timeout:
            while True:
                if self.is_rpc_ready:
                    break
                time.sleep(0.1)
                _timeout.check()

    @property
    def ipc_enabled(self) -> bool:
        return not self.geth_kwargs.get("ipc_disable", None)

    @property
    def ipc_path(self) -> str:
        return self.geth_kwargs.get("ipc_path") or os.path.abspath(
            os.path.expanduser(
                os.path.join(
                    self.data_dir,
                    "geth.ipc",
                )
            )
        )

    @property
    def is_ipc_ready(self) -> bool:
        try:
            with get_ipc_socket(self.ipc_path):
                pass
        except OSError:
            return False
        else:
            return True

    def wait_for_ipc(self, timeout: int = 0) -> None:
        if not self.ipc_enabled:
            raise PyGethValueError("IPC interface is not enabled")

        with Timeout(timeout) as _timeout:
            while True:
                if self.is_ipc_ready:
                    break
                time.sleep(0.1)
                _timeout.check()

    @property
    def version(self) -> str:
        return str(get_geth_version(**self.geth_kwargs))


class MainnetGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs: GethKwargsTypedDict | None = None):
        if geth_kwargs is None:
            geth_kwargs = {}

        if "data_dir" in geth_kwargs:
            raise PyGethValueError(
                "You cannot specify `data_dir` for a MainnetGethProcess"
            )

        super().__init__(geth_kwargs)

    @property
    def data_dir(self) -> str:
        return get_live_data_dir()


class SepoliaGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs: GethKwargsTypedDict | None = None):
        if geth_kwargs is None:
            geth_kwargs = {}

        if "data_dir" in geth_kwargs:
            raise PyGethValueError(
                f"You cannot specify `data_dir` for a {type(self).__name__}"
            )
        if "network_id" in geth_kwargs:
            raise PyGethValueError(
                f"You cannot specify `network_id` for a {type(self).__name__}"
            )

        geth_kwargs["network_id"] = "11155111"
        geth_kwargs["data_dir"] = get_sepolia_data_dir()

        super().__init__(geth_kwargs)

    @property
    def data_dir(self) -> str:
        return get_sepolia_data_dir()


class TestnetGethProcess(SepoliaGethProcess):
    """
    Alias for whatever the current primary testnet chain is.
    """


class DevGethProcess(BaseGethProcess):
    """
    Geth developer mode process for testing purposes.
    """

    _data_dir: str

    def __init__(
        self,
        chain_name: str,
        base_dir: str | None = None,
        overrides: GethKwargsTypedDict | None = None,
        genesis_data: GenesisDataTypedDict | None = None,
    ):
        if overrides is None:
            overrides = {}

        if genesis_data is None:
            # deepcopy since we may modify the data on init below
            genesis_data = GenesisDataTypedDict(**copy.deepcopy(GENESIS_JSON))

        validate_genesis_data(genesis_data)

        if "data_dir" in overrides:
            raise PyGethValueError("You cannot specify `data_dir` for a DevGethProcess")

        if base_dir is None:
            base_dir = get_default_base_dir()

        self._data_dir = get_chain_data_dir(base_dir, chain_name)
        overrides["data_dir"] = self.data_dir
        geth_kwargs = construct_test_chain_kwargs(**overrides)
        validate_geth_kwargs(geth_kwargs)

        # ensure that an account is present
        coinbase = ensure_account_exists(**geth_kwargs)

        # ensure that the chain is initialized
        genesis_file_path = get_genesis_file_path(self.data_dir)
        needs_init = all(
            (
                not os.path.exists(genesis_file_path),
                not is_live_chain(self.data_dir),
                not is_sepolia_chain(self.data_dir),
            )
        )
        if needs_init:
            genesis_data["coinbase"] = coinbase
            genesis_data.setdefault("alloc", {}).setdefault(
                coinbase, {"balance": "1000000000000000000000000000000"}
            )

            modify_genesis_based_on_geth_version(genesis_data)
            initialize_chain(genesis_data, self.data_dir)

        super().__init__(geth_kwargs)

    @property
    def data_dir(self) -> str:
        return self._data_dir


def modify_genesis_based_on_geth_version(genesis_data: GenesisDataTypedDict) -> None:
    geth_version = get_geth_version()
    if geth_version <= semantic_version.Version("1.14.0"):
        # geth <= v1.14.0 needs negative `terminalTotalDifficulty` to load EVM
        # instructions correctly: https://github.com/ethereum/go-ethereum/pull/29579
        if "config" not in genesis_data:
            genesis_data["config"] = {}
        genesis_data["config"]["terminalTotalDifficulty"] = -1
