from __future__ import (
    annotations,
)

import os

from typing_extensions import (
    Unpack,
)

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GethKwargsTypedDict,
)
from geth.utils.validation import (
    validate_geth_kwargs,
)

from .chains import (
    is_live_chain,
    is_testnet_chain,
)
from .utils.filesystem import (
    remove_dir_if_exists,
    remove_file_if_exists,
)
from .wrapper import (
    spawn_geth,
)


def soft_reset_chain(
    allow_live: bool = False,
    allow_testnet: bool = False,
    **geth_kwargs: Unpack[GethKwargsTypedDict],
) -> None:
    validate_geth_kwargs(geth_kwargs)
    data_dir = geth_kwargs.get("data_dir")

    if data_dir is None or (not allow_live and is_live_chain(data_dir)):
        raise PyGethValueError(
            "To reset the live chain you must call this function with `allow_live=True`"
        )

    if not allow_testnet and is_testnet_chain(data_dir):
        raise PyGethValueError(
            "To reset the testnet chain you must call this function with `allow_testnet=True`"  # noqa: E501
        )

    suffix_args = geth_kwargs.pop("suffix_args") or []
    suffix_args.extend(("removedb",))
    geth_kwargs.update({"suffix_args": suffix_args})

    _, proc = spawn_geth(geth_kwargs)

    stdoutdata, stderrdata = proc.communicate(b"y")

    if "Removing chaindata" not in stdoutdata.decode():
        raise PyGethValueError(
            "An error occurred while removing the chain:\n\nError:\n"
            f"{stderrdata.decode()}\n\nOutput:\n{stdoutdata.decode()}"
        )


def hard_reset_chain(
    data_dir: str, allow_live: bool = False, allow_testnet: bool = False
) -> None:
    if not allow_live and is_live_chain(data_dir):
        raise PyGethValueError(
            "To reset the live chain you must call this function with `allow_live=True`"
        )

    if not allow_testnet and is_testnet_chain(data_dir):
        raise PyGethValueError(
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
