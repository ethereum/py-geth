import json
import os
import sys

from .utils.encoding import (
    force_obj_to_text,
)
from .utils.filesystem import (
    ensure_path_exists,
    is_same_path,
)
from .wrapper import (
    spawn_geth,
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
    nonce="0xdeadbeefdeadbeef",
    timestamp="0x0",
    parentHash="0x0000000000000000000000000000000000000000000000000000000000000000",
    extraData=None,
    gasLimit="0x47d5cc",
    difficulty="0x01",
    mixhash="0x0000000000000000000000000000000000000000000000000000000000000000",
    coinbase="0x3333333333333333333333333333333333333333",
    alloc=None,
    config=None,
    clique_period: int = 5,
    clique_epoch: int = 30000,
):
    if os.path.exists(genesis_file_path) and not overwrite:
        raise ValueError(
            "Genesis file already present.  call with `overwrite=True` to overwrite this file"  # noqa: E501
        )

    if alloc is None:
        alloc = {}

    if config is None:
        config = {
            "homesteadBlock": 0,
            "eip150Block": 0,
            "eip155Block": 0,
            "eip158Block": 0,
            "byzantiumBlock": 0,
            "constantinopleBlock": 0,
            "petersburgBlock": 0,
            "istanbulBlock": 0,
            "berlinBlock": 0,
            "londonBlock": 0,
            "shanghaiBlock": 0,
            "daoForkBlock": 0,
            "daoForSupport": True,
            # Using the Ethash consensus algorithm is deprecated
            # Instead, use the Clique consensus algorithm
            # https://geth.ethereum.org/docs/fundamentals/private-network
            "clique": {"period": clique_period, "epoch": clique_epoch},
        }

    # Assign a signer (coinbase) to the genesis block for Clique
    extraData = (
        bytes("0x" + "0" * 64 + coinbase[2:] + "0" * 130, "ascii")
        if extraData is None
        else extraData
    )

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


def initialize_chain(genesis_data, data_dir, **geth_kwargs):
    genesis_file_path = get_genesis_file_path(data_dir)
    write_genesis_file(genesis_file_path, **genesis_data)
    command, proc = spawn_geth(
        dict(data_dir=data_dir, suffix_args=["init", genesis_file_path], **geth_kwargs)
    )
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode:
        raise ValueError(f"Error: {stdoutdata + stderrdata}")
