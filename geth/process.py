from __future__ import (
    annotations,
)

import logging
import os
import subprocess
import time
from types import (
    TracebackType,
)
from typing import (
    Any,
    cast,
)
from urllib.error import (
    URLError,
)
from urllib.request import (
    urlopen,
)
import warnings

from geth.accounts import (
    ensure_account_exists,
    get_accounts,
)
from geth.chain import (
    get_chain_data_dir,
    get_default_base_dir,
    get_genesis_file_path,
    get_live_data_dir,
    get_ropsten_data_dir,
    initialize_chain,
    is_live_chain,
    is_ropsten_chain,
)
from geth.models import (
    GenesisData,
    GethKwargs,
)
from geth.types import (
    IO_Any,
)
from geth.utils.dag import (
    is_dag_generated,
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
from geth.wrapper import (
    construct_popen_command,
    construct_test_chain_kwargs,
)

logger = logging.getLogger(__name__)


class BaseGethProcess:
    _proc = None

    def __init__(
        self,
        geth_kwargs: GethKwargs,
        stdin: IO_Any = subprocess.PIPE,
        stdout: IO_Any = subprocess.PIPE,
        stderr: IO_Any = subprocess.PIPE,
    ):
        # breakpoint()
        self.geth_kwargs = geth_kwargs
        self.command = construct_popen_command(geth_kwargs)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    is_running = False

    def start(self) -> None:
        if self.is_running:
            raise ValueError("Already running")
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
            raise ValueError("Not running")

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
    def is_alive(self) -> bool:
        return self.is_running and self.proc.poll() is None

    @property
    def is_stopped(self) -> bool:
        return self.proc is not None and self.proc.poll() is not None

    @property
    def accounts(self) -> tuple[bytes, ...]:
        if not self.geth_kwargs.data_dir:
            raise ValueError("Cannot determine accounts without a `data_dir`")
        return get_accounts(self.geth_kwargs.data_dir, self.geth_kwargs)

    @property
    def rpc_enabled(self) -> bool:
        return getattr(self.geth_kwargs, "rpc_enabled", False)

    @property
    def rpc_host(self) -> str:
        return getattr(self.geth_kwargs, "rpc_host", "127.0.0.1")

    @property
    def rpc_port(self) -> str:
        return getattr(self.geth_kwargs, "rpc_port", "8545")

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
            raise ValueError("RPC interface is not enabled")

        with Timeout(timeout) as _timeout:
            while True:
                if self.is_rpc_ready:
                    break
                time.sleep(0.1)
                _timeout.check()

    @property
    def ipc_enabled(self) -> bool:
        return not getattr(self.geth_kwargs, "ipc_disable", None)

    @property
    def ipc_path(self) -> str:
        if not self.geth_kwargs.data_dir:
            raise ValueError("Cannot determine IPC path without a `data_dir`")
        return getattr(
            self.geth_kwargs,
            "ipc_path",
            os.path.abspath(
                os.path.expanduser(
                    os.path.join(
                        self.geth_kwargs.data_dir,
                        "geth.ipc",
                    )
                )
            ),
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
            raise ValueError("IPC interface is not enabled")

        with Timeout(timeout) as _timeout:
            while True:
                if self.is_ipc_ready:
                    break
                time.sleep(0.1)
                _timeout.check()

    @property
    def is_dag_generated(self) -> bool:
        return is_dag_generated()

    @property
    def is_mining(self) -> bool:
        mine_bool = cast(bool, self.geth_kwargs.mine)
        return mine_bool

    def wait_for_dag(self, timeout: int = 0) -> None:
        if not self.is_mining and not self.geth_kwargs.autodag:
            raise ValueError("Geth not configured to generate DAG")

        with Timeout(timeout) as _timeout:
            while True:
                if self.is_dag_generated:
                    break
                time.sleep(0.1)
                _timeout.check()


class MainnetGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs: GethKwargs | None = None):
        if geth_kwargs is None:
            geth_kwargs = GethKwargs()

        if geth_kwargs.data_dir:
            raise ValueError("You cannot specify `data_dir` for a MainnetGethProcess")

        super().__init__(geth_kwargs)

    @property
    def data_dir(self) -> str:
        return get_live_data_dir()


class LiveGethProcess(MainnetGethProcess):
    def __init__(self, *args: Any, **kwargs: Any):
        warnings.warn(
            DeprecationWarning(
                "The `LiveGethProcess` has been renamed to `MainnetGethProcess`. "
                "The `LiveGethProcess` alias will be removed in subsequent releases"
            ),
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class RopstenGethProcess(BaseGethProcess):
    def __init__(self, geth_kwargs: GethKwargs | None = None):
        if geth_kwargs is None:
            geth_kwargs = GethKwargs()

        if geth_kwargs.data_dir:
            raise ValueError(
                f"You cannot specify `data_dir` for a {type(self).__name__}"
            )
        if geth_kwargs.network_id:
            raise ValueError(
                f"You cannot specify `network_id` for a {type(self).__name__}"
            )

        geth_kwargs.network_id = "3"
        geth_kwargs.data_dir = get_ropsten_data_dir()

        super().__init__(geth_kwargs)

    @property
    def data_dir(self) -> str:
        return get_ropsten_data_dir()


class TestnetGethProcess(RopstenGethProcess):
    """
    Alias for whatever the current primary testnet chain is.
    """


class DevGethProcess(BaseGethProcess):
    """
    A local private chain for development.
    """

    def __init__(
        self,
        chain_name: str,
        base_dir: str | None = None,
        overrides: GethKwargs | None = None,
        genesis_data: GenesisData | None = None,
    ):
        if overrides is None:
            overrides = GethKwargs()

        if genesis_data is None:
            genesis_data = GenesisData()

        if getattr(overrides, "data_dir", None):
            raise ValueError("You cannot specify `data_dir` for a DevGethProcess")

        if base_dir is None:
            base_dir = get_default_base_dir()

        self.data_dir = get_chain_data_dir(base_dir, chain_name)
        overrides.data_dir = self.data_dir
        geth_kwargs: GethKwargs = construct_test_chain_kwargs(overrides)

        # ensure that an account is present
        coinbase = ensure_account_exists(self.data_dir, geth_kwargs)

        # ensure that the chain is initialized
        genesis_file_path = get_genesis_file_path(self.data_dir)

        needs_init = all(
            (
                not os.path.exists(genesis_file_path),
                not is_live_chain(self.data_dir),
                not is_ropsten_chain(self.data_dir),
            )
        )

        if needs_init:
            if not genesis_data.alloc:
                genesis_data.alloc = dict(
                    [
                        (
                            coinbase,
                            {
                                "balance": "1000000000000000000000000000000"  # 1 billion ether  # noqa: E501
                            },
                        ),
                    ]
                )

                initialize_chain(genesis_data, self.data_dir, geth_kwargs)

        super().__init__(geth_kwargs)
