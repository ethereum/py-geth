import os
from typing import (
    Any,
)

from geth.models import (
    GethKwargs,
)

from .chain import (
    is_live_chain,
    is_ropsten_chain,
)
from .utils.filesystem import (
    remove_dir_if_exists,
    remove_file_if_exists,
)
from .wrapper import (
    spawn_geth,
)

# TODO is this file still relevant? Not referenced or used or tested anywhere


def soft_reset_chain(
    geth_kwargs: GethKwargs, allow_live: bool = False, allow_testnet: bool = False
) -> None:
    data_dir = getattr(geth_kwargs, "data_dir", None)

    if data_dir is None or (not allow_live and is_live_chain(data_dir)):
        raise ValueError(
            "To reset the live chain you must call this function with `allow_live=True`"
        )

    if not allow_testnet and is_ropsten_chain(data_dir):
        raise ValueError(
            "To reset the testnet chain you must call this function with `allow_testnet=True`"  # noqa: E501
        )

    suffix_args = getattr(geth_kwargs, "suffix_args", [])
    suffix_args.extend(("removedb",))
    geth_kwargs.suffix_args = suffix_args

    _, proc = spawn_geth(geth_kwargs)

    stdoutdata, stderrdata = proc.communicate(b"y")

    if "Removing chaindata" not in stdoutdata.decode("utf-8"):
        raise ValueError(
            "An error occurred while removing the chain:\n\nError:\n"
            f"{stderrdata.decode('utf-8')}\n\nOutput:\n{stdoutdata.decode('utf-8')}"
        )


def hard_reset_chain(
    data_dir: str, allow_live: bool = False, allow_testnet: bool = False
) -> None:
    if not allow_live and is_live_chain(data_dir):
        raise ValueError(
            "To reset the live chain you must call this function with `allow_live=True`"
        )

    if not allow_testnet and is_ropsten_chain(data_dir):
        raise ValueError(
            "To reset the testnet chain you must call this function with `allow_testnet=True`"  # noqa: E501
        )

    blockchain_dir = os.path.join(data_dir, "chaindata")
    remove_dir_if_exists(blockchain_dir)

    dapp_dir = os.path.join(data_dir, "dapp")
    remove_dir_if_exists(dapp_dir)

    nodekey_path = os.path.join(data_dir, "nodekey")
    remove_file_if_exists(nodekey_path)

    nodes_path = os.path.join(data_dir, "nodes")
    remove_dir_if_exists(nodes_path)

    geth_ipc_path = os.path.join(data_dir, "geth.ipc")
    remove_file_if_exists(geth_ipc_path)

    history_path = os.path.join(data_dir, "history")
    remove_file_if_exists(history_path)
