from __future__ import (
    annotations,
)

import json
import os
import subprocess
import sys

from typing_extensions import (
    Unpack,
)

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GenesisDataTypedDict,
)

from .utils.encoding import (
    force_obj_to_text,
)
from .utils.filesystem import (
    ensure_path_exists,
    is_same_path,
)
from .utils.validation import (
    validate_genesis_data,
)
from .wrapper import (
    get_geth_binary_path,
)


def get_live_data_dir() -> str:
    """
    `py-geth` needs a base directory to store it's chain data.  By default this is
    the directory that `geth` uses as it's `datadir`.
    """
    if sys.platform == "darwin":
        data_dir = os.path.expanduser(
            os.path.join(
                "~",
                "Library",
                "Ethereum",
            )
        )
    elif sys.platform in {"linux", "linux2", "linux3"}:
        data_dir = os.path.expanduser(
            os.path.join(
                "~",
                ".ethereum",
            )
        )
    elif sys.platform == "win32":
        data_dir = os.path.expanduser(
            os.path.join(
                "\\",
                "~",
                "AppData",
                "Roaming",
                "Ethereum",
            )
        )

    else:
        raise PyGethValueError(
            f"Unsupported platform: '{sys.platform}'.  Only darwin/linux2/win32 are"
            " supported.  You must specify the geth datadir manually"
        )
    return data_dir


def get_sepolia_data_dir() -> str:
    return os.path.abspath(
        os.path.expanduser(
            os.path.join(
                get_live_data_dir(),
                "sepolia",
            )
        )
    )


def get_default_base_dir() -> str:
    return get_live_data_dir()


def get_chain_data_dir(base_dir: str, name: str) -> str:
    data_dir = os.path.abspath(os.path.join(base_dir, name))
    ensure_path_exists(data_dir)
    return data_dir


def get_genesis_file_path(data_dir: str) -> str:
    return os.path.join(data_dir, "genesis.json")


def is_live_chain(data_dir: str) -> bool:
    return is_same_path(data_dir, get_live_data_dir())


def is_sepolia_chain(data_dir: str) -> bool:
    return is_same_path(data_dir, get_sepolia_data_dir())


def write_genesis_file(
    genesis_file_path: str,
    overwrite: bool = False,
    **genesis_data: Unpack[GenesisDataTypedDict],
) -> None:
    if os.path.exists(genesis_file_path) and not overwrite:
        raise PyGethValueError(
            "Genesis file already present. Call with "
            "`overwrite=True` to overwrite this file"
        )

    validate_genesis_data(genesis_data)

    with open(genesis_file_path, "w") as genesis_file:
        genesis_file.write(force_obj_to_text(json.dumps(genesis_data)))


def initialize_chain(genesis_data: GenesisDataTypedDict, data_dir: str) -> None:
    validate_genesis_data(genesis_data)
    # init with genesis.json
    genesis_file_path = get_genesis_file_path(data_dir)
    write_genesis_file(genesis_file_path, **genesis_data)
    init_proc = subprocess.Popen(
        (
            get_geth_binary_path(),
            "--datadir",
            data_dir,
            "init",
            genesis_file_path,
        ),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdoutdata, stderrdata = init_proc.communicate()
    init_proc.wait()
    if init_proc.returncode:
        raise PyGethValueError(
            "Error initializing genesis.json: \n"
            f"    stdout={stdoutdata.decode()}\n"
            f"    stderr={stderrdata.decode()}"
        )
