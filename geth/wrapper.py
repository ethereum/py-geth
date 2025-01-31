from __future__ import (
    annotations,
)

import functools
import os
import subprocess
import sys
import tempfile
from typing import (
    Any,
    Iterable,
    cast,
)

from typing_extensions import (
    Unpack,
)

from geth.exceptions import (
    PyGethGethError,
    PyGethValueError,
)
from geth.types import (
    GethKwargsTypedDict,
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
from geth.utils.validation import (
    GethKwargs,
    validate_geth_kwargs,
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


def construct_test_chain_kwargs(
    **overrides: Unpack[GethKwargsTypedDict],
) -> GethKwargsTypedDict:
    validate_geth_kwargs(overrides)
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
        if overrides.get("data_dir") is not None:
            data_dir = cast(str, overrides["data_dir"])
            max_path_length = get_max_socket_path_length()
            geth_ipc_path = os.path.abspath(os.path.join(data_dir, "geth.ipc"))
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


def construct_popen_command(**geth_kwargs: Unpack[GethKwargsTypedDict]) -> list[str]:
    # validate geth_kwargs and fill defaults that may not have been provided
    validate_geth_kwargs(geth_kwargs)
    gk = GethKwargs(**geth_kwargs)

    if gk.geth_executable is None:
        gk.geth_executable = get_geth_binary_path()

    if not is_executable_available(gk.geth_executable):
        raise PyGethValueError(
            "No geth executable found.  Please ensure geth is installed and "
            "available on your PATH or use the GETH_BINARY environment variable"
        )

    builder = CommandBuilder()

    if gk.nice and is_nice_available():
        builder.extend(("nice", "-n", "20"))

    builder.append(gk.geth_executable)

    if gk.dev_mode:
        builder.append("--dev")

    if gk.dev_period is not None:
        builder.extend(("--dev.period", gk.dev_period))

    if gk.rpc_enabled:
        builder.append("--http")

    if gk.rpc_addr is not None:
        builder.extend(("--http.addr", gk.rpc_addr))

    if gk.rpc_port is not None:
        builder.extend(("--http.port", gk.rpc_port))

    if gk.rpc_api is not None:
        builder.extend(("--http.api", gk.rpc_api))

    if gk.rpc_cors_domain is not None:
        builder.extend(("--http.corsdomain", gk.rpc_cors_domain))

    if gk.ws_enabled:
        builder.append("--ws")

    if gk.ws_addr is not None:
        builder.extend(("--ws.addr", gk.ws_addr))

    if gk.ws_origins is not None:
        builder.extend(("--ws.origins", gk.ws_port))

    if gk.ws_port is not None:
        builder.extend(("--ws.port", gk.ws_port))

    if gk.ws_api is not None:
        builder.extend(("--ws.api", gk.ws_api))

    if gk.data_dir is not None:
        builder.extend(("--datadir", gk.data_dir))

    if gk.max_peers is not None:
        builder.extend(("--maxpeers", gk.max_peers))

    if gk.network_id is not None:
        builder.extend(("--networkid", gk.network_id))

    if gk.port is not None:
        builder.extend(("--port", gk.port))

    if gk.ipc_disable:
        builder.append("--ipcdisable")

    if gk.ipc_path is not None:
        builder.extend(("--ipcpath", gk.ipc_path))

    if gk.verbosity is not None:
        builder.extend(("--verbosity", gk.verbosity))

    if isinstance(gk.password, str) and gk.password is not None:
        # If password is a string, it's a file path
        # If password is bytes, it's the password itself and is passed directly to
        # the geth process elsewhere
        builder.extend(("--password", gk.password))

    if gk.preload is not None:
        builder.extend(("--preload", gk.preload))

    if gk.no_discover:
        builder.append("--nodiscover")

    if gk.tx_pool_global_slots is not None:
        builder.extend(("--txpool.globalslots", gk.tx_pool_global_slots))

    if gk.tx_pool_lifetime is not None:
        builder.extend(("--txpool.lifetime", gk.tx_pool_lifetime))

    if gk.tx_pool_price_limit is not None:
        builder.extend(("--txpool.pricelimit", gk.tx_pool_price_limit))

    if gk.cache:
        builder.extend(("--cache", gk.cache))

    if gk.gcmode:
        builder.extend(("--gcmode", gk.gcmode))

    if gk.suffix_kwargs:
        builder.extend(gk.suffix_kwargs)

    if gk.suffix_args:
        builder.extend(gk.suffix_args)

    return builder.command


def geth_wrapper(
    **geth_kwargs: Unpack[GethKwargsTypedDict],
) -> tuple[bytes, bytes, list[str], subprocess.Popen[bytes]]:
    validate_geth_kwargs(geth_kwargs)
    stdin = geth_kwargs.pop("stdin", None)
    command = construct_popen_command(**geth_kwargs)

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdin_bytes: bytes | None = None
    if stdin is not None:
        stdin_bytes = force_bytes(stdin)

    stdoutdata, stderrdata = proc.communicate(stdin_bytes)

    if proc.returncode != 0:
        raise PyGethGethError(
            command=command,
            return_code=proc.returncode,
            stdin_data=stdin,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )

    return stdoutdata, stderrdata, command, proc


def spawn_geth(
    geth_kwargs: GethKwargsTypedDict,
    stdin: IO_Any = subprocess.PIPE,
    stdout: IO_Any = subprocess.PIPE,
    stderr: IO_Any = subprocess.PIPE,
) -> tuple[list[str], subprocess.Popen[bytes]]:
    validate_geth_kwargs(geth_kwargs)
    command = construct_popen_command(**geth_kwargs)

    proc = subprocess.Popen(
        command,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )

    return command, proc
