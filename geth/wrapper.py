from __future__ import (
    annotations,
)

import functools
import logging
import os
import subprocess
import sys
import tempfile
from typing import (
    Any,
    Iterable,
)

from geth.exceptions import (
    GethError,
)
from geth.models import (
    GethKwargs,
)
from geth.types import (
    IO_Any,
)
from geth.utils.encoding import (
    force_bytes,
)
from geth.utils.filesystem import (
    is_executable_available,
)
from geth.utils.networking import (
    get_open_port,
    is_port_open,
)

is_nice_available = functools.partial(is_executable_available, "nice")


PYGETH_DIR = os.path.abspath(os.path.dirname(__file__))


DEFAULT_PASSWORD_PATH = os.path.join(PYGETH_DIR, "default_blockchain_password")


ALL_APIS = "admin,debug,eth,net,txpool,web3"


def get_max_socket_path_length() -> int:
    if "UNIX_PATH_MAX" in os.environ:
        return int(os.environ["UNIX_PATH_MAX"])
    if sys.platform.startswith("darwin"):
        return 104
    elif sys.platform.startswith("linux"):
        return 108
    elif sys.platform.startswith("win"):
        return 260


def construct_test_chain_kwargs(**overrides: Any) -> dict[str, Any]:
    overrides.setdefault("dev_mode", True)
    overrides.setdefault("password", DEFAULT_PASSWORD_PATH)
    overrides.setdefault("no_discover", True)
    overrides.setdefault("max_peers", "0")
    overrides.setdefault("network_id", "1234")

    if is_port_open(30303):
        overrides.setdefault("port", "30303")
    else:
        overrides.setdefault("port", get_open_port())

    overrides.setdefault("ws_enabled", True)
    overrides.setdefault("ws_api", ALL_APIS)

    if is_port_open(8546):
        overrides.setdefault("ws_port", "8546")
    else:
        overrides.setdefault("ws_port", get_open_port())

    overrides.setdefault("rpc_enabled", True)
    overrides.setdefault("rpc_api", ALL_APIS)
    if is_port_open(8545):
        overrides.setdefault("rpc_port", "8545")
    else:
        overrides.setdefault("rpc_port", get_open_port())

    if "ipc_path" not in overrides:
        # try to use a `geth.ipc` within the provided data_dir if the path is
        # short enough.
        if "data_dir" in overrides:
            max_path_length = get_max_socket_path_length()
            geth_ipc_path = os.path.abspath(
                os.path.join(overrides["data_dir"], "geth.ipc")
            )
            if len(geth_ipc_path) <= max_path_length:
                overrides.setdefault("ipc_path", geth_ipc_path)

        # Otherwise default to a tempfile based ipc path.
        overrides.setdefault(
            "ipc_path",
            os.path.join(tempfile.mkdtemp(), "geth.ipc"),
        )

    overrides.setdefault("verbosity", "5")

    return overrides


def get_geth_binary_path() -> str:
    return os.environ.get("GETH_BINARY", "geth")


class CommandBuilder:
    def __init__(self) -> None:
        self.command: list[str] = []

    def append(self, value: Any) -> None:
        self.command.append(str(value))

    def extend(self, value_list: Iterable[Any]) -> None:
        self.command.extend([str(v) for v in value_list])


def construct_popen_command(
    geth_kwargs: GethKwargs,
    # data_dir=None,
    # dev_mode=None,
    # geth_executable=None,
    # max_peers=None,
    # network_id=None,
    # no_discover=None,
    # mine=False,
    # autodag=False,
    # miner_threads=None,  # deprecated
    # miner_etherbase=None,
    # nice=True,
    # unlock=None,
    # password=None,
    # preload=None,
    # port=None,
    # verbosity=None,
    # ipc_disable=None,
    # ipc_path=None,
    # ipc_disabled=None,
    # rpc_enabled=None,
    # rpc_addr=None,
    # rpc_port=None,
    # rpc_api=None,
    # rpc_cors_domain=None,
    # ws_enabled=None,
    # ws_addr=None,
    # ws_origins=None,
    # ws_port=None,
    # ws_api=None,
    # suffix_args=None,
    # suffix_kwargs=None,
    # shh=None,
    # allow_insecure_unlock=None,
    # tx_pool_global_slots=None,
    # tx_pool_price_limit=None,
    # cache=None,
    # gcmode=None,
) -> list[str]:
    if geth_kwargs.geth_executable is None:
        geth_kwargs.geth_executable = get_geth_binary_path()

    if not is_executable_available(geth_kwargs.geth_executable):
        raise ValueError(
            "No geth executable found.  Please ensure geth is installed and "
            "available on your PATH or use the GETH_BINARY environment variable"
        )

    builder = CommandBuilder()

    if geth_kwargs.nice and is_nice_available():
        builder.extend(("nice", "-n", "20"))

    builder.append(geth_kwargs.geth_executable)

    if geth_kwargs.dev_mode:
        builder.append("--dev")

    if geth_kwargs.rpc_enabled:
        builder.append("--http")

    if geth_kwargs.rpc_addr is not None:
        builder.extend(("--http.addr", geth_kwargs.rpc_addr))

    if geth_kwargs.rpc_port is not None:
        builder.extend(("--http.port", geth_kwargs.rpc_port))

    if geth_kwargs.rpc_api is not None:
        builder.extend(("--http.api", geth_kwargs.rpc_api))

    if geth_kwargs.rpc_cors_domain is not None:
        builder.extend(("--http.corsdomain", geth_kwargs.rpc_cors_domain))

    if geth_kwargs.ws_enabled:
        builder.append("--ws")

    if geth_kwargs.ws_addr is not None:
        builder.extend(("--ws.addr", geth_kwargs.ws_addr))

    if geth_kwargs.ws_origins is not None:
        builder.extend(("--ws.origins", geth_kwargs.ws_port))

    if geth_kwargs.ws_port is not None:
        builder.extend(("--ws.port", geth_kwargs.ws_port))

    if geth_kwargs.ws_api is not None:
        builder.extend(("--ws.api", geth_kwargs.ws_api))

    if geth_kwargs.data_dir is not None:
        builder.extend(("--datadir", geth_kwargs.data_dir))

    if geth_kwargs.max_peers is not None:
        builder.extend(("--maxpeers", geth_kwargs.max_peers))

    if geth_kwargs.network_id is not None:
        builder.extend(("--networkid", geth_kwargs.network_id))

    if geth_kwargs.port is not None:
        builder.extend(("--port", geth_kwargs.port))

    if geth_kwargs.ipc_disable:
        builder.append("--ipcdisable")

    if geth_kwargs.ipc_path is not None:
        builder.extend(("--ipcpath", geth_kwargs.ipc_path))

    if geth_kwargs.verbosity is not None:
        builder.extend(
            (
                "--verbosity",
                geth_kwargs.verbosity,
            )
        )

    if geth_kwargs.unlock is not None:
        builder.extend(
            (
                "--unlock",
                geth_kwargs.unlock,
            )
        )

    if geth_kwargs.password is not None:
        builder.extend(
            (
                "--password",
                geth_kwargs.password,
            )
        )

    if geth_kwargs.preload is not None:
        builder.extend(("--preload", geth_kwargs.preload))

    if geth_kwargs.no_discover:
        builder.append("--nodiscover")

    if geth_kwargs.mine:
        if geth_kwargs.unlock is None:
            raise ValueError("Cannot mine without an unlocked account")
        builder.append("--mine")

    if geth_kwargs.miner_threads is not None:
        logging.warning(
            "`--miner.threads` is deprecated and will be removed in a future release."
        )
        if not geth_kwargs.mine:
            raise ValueError("`mine` must be truthy when specifying `miner_threads`")
        builder.extend(("--miner.threads", geth_kwargs.miner_threads))

    if geth_kwargs.miner_etherbase is not None:
        if not geth_kwargs.mine:
            raise ValueError("`mine` must be truthy when specifying `miner_etherbase`")
        builder.extend(("--miner.etherbase", geth_kwargs.miner_etherbase))

    if geth_kwargs.autodag:
        builder.append("--autodag")

    if geth_kwargs.shh:
        builder.append("--shh")

    if geth_kwargs.allow_insecure_unlock:
        builder.append("--allow-insecure-unlock")

    if geth_kwargs.tx_pool_global_slots is not None:
        builder.extend(("--txpool.globalslots", geth_kwargs.tx_pool_global_slots))

    if geth_kwargs.tx_pool_price_limit is not None:
        builder.extend(("--txpool.pricelimit", geth_kwargs.tx_pool_price_limit))

    if geth_kwargs.cache:
        builder.extend(("--cache", geth_kwargs.cache))

    if geth_kwargs.gcmode:
        builder.extend(("--gcmode", geth_kwargs.gcmode))

    if geth_kwargs.suffix_kwargs:
        builder.extend(geth_kwargs.suffix_kwargs)

    if geth_kwargs.suffix_args:
        builder.extend(geth_kwargs.suffix_args)

    return builder.command


def geth_wrapper(
    geth_kwargs: GethKwargs,
) -> tuple[bytes, bytes, list[str], subprocess.Popen[bytes]]:
    stdin: str | bytes | None = geth_kwargs.stdin or None
    command = construct_popen_command(geth_kwargs)

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if stdin is not None:
        stdin = force_bytes(stdin)

    stdoutdata, stderrdata = proc.communicate(stdin)

    if proc.returncode != 0:
        raise GethError(
            command=command,
            return_code=proc.returncode,
            stdin_data=stdin,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )

    return stdoutdata, stderrdata, command, proc


def spawn_geth(
    geth_kwargs: GethKwargs,
    stdin: IO_Any = subprocess.PIPE,
    stdout: IO_Any = subprocess.PIPE,
    stderr: IO_Any = subprocess.PIPE,
) -> tuple[list[str], subprocess.Popen[bytes]]:
    command = construct_popen_command(geth_kwargs)

    proc = subprocess.Popen(
        command,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )

    return command, proc
