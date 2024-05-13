import json
import os
import subprocess
import sys

from .utils.encoding import (
    force_obj_to_text,
)
from .utils.filesystem import (
    ensure_path_exists,
    is_same_path,
)
from .wrapper import (
    get_geth_binary_path,
)


def get_live_data_dir():
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
        raise ValueError(
            f"Unsupported platform: '{sys.platform}'.  Only darwin/linux2/win32 are"
            " supported.  You must specify the geth datadir manually"
        )
    return data_dir


def get_ropsten_data_dir():
    return os.path.abspath(
        os.path.expanduser(
            os.path.join(
                get_live_data_dir(),
                "ropsten",
            )
        )
    )


def get_default_base_dir():
    return get_live_data_dir()


def get_chain_data_dir(base_dir, name):
    data_dir = os.path.abspath(os.path.join(base_dir, name))
    ensure_path_exists(data_dir)
    return data_dir


def get_genesis_file_path(data_dir):
    return os.path.join(data_dir, "genesis.json")


def is_live_chain(data_dir):
    return is_same_path(data_dir, get_live_data_dir())


def is_ropsten_chain(data_dir):
    return is_same_path(data_dir, get_ropsten_data_dir())


def write_genesis_file(
    genesis_file_path,
    overwrite=False,
    nonce="0x0",
    timestamp="0x0",
    parentHash="0x0000000000000000000000000000000000000000000000000000000000000000",
    extraData="0x0000000000000000000000000000000000000000000000000000000000000000",
    gasLimit="0x47d5cc",
    difficulty="0x0",
    mixhash="0x0000000000000000000000000000000000000000000000000000000000000000",
    coinbase="0x3333333333333333333333333333333333333333",
    alloc=None,
    config=None,
):
    if os.path.exists(genesis_file_path) and not overwrite:
        raise ValueError(
            "Genesis file already present.  call with `overwrite=True` to overwrite this file"  # noqa: E501
        )

    if alloc is None:
        alloc = {}

    if config is None:
        config = {
            "ethash": {},
            "homesteadBlock": 0,
            "daoForkBlock": 0,
            "daoForkSupport": True,
            "eip150Block": 0,
            "eip155Block": 0,
            "eip158Block": 0,
            "byzantiumBlock": 0,
            "constantinopleBlock": 0,
            "petersburgBlock": 0,
            "istanbulBlock": 0,
            "berlinBlock": 0,
            "londonBlock": 0,
            "arrowGlacierBlock": 0,
            "grayGlacierBlock": 0,
            # merge
            "terminalTotalDifficulty": 0,
            "terminalTotalDifficultyPassed": True,
            # post-merge, timestamp is used for network transitions
            "shanghaiTime": 0,
            "cancunTime": 0,
        }

    genesis_data = {
        "nonce": nonce,
        "timestamp": timestamp,
        "parentHash": parentHash,
        "extraData": extraData,
        "gasLimit": gasLimit,
        "difficulty": difficulty,
        "mixhash": mixhash,
        "coinbase": coinbase,
        "alloc": alloc,
        "config": config,
    }

    with open(genesis_file_path, "w") as genesis_file:
        genesis_file.write(json.dumps(force_obj_to_text(genesis_data)))


def initialize_chain(genesis_data, data_dir):
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
        raise ValueError(
            "Error initializing genesis.json: \n"
            f"    stdout={stdoutdata}\n"
            f"    stderr={stderrdata}"
        )
