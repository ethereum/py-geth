from __future__ import (
    annotations,
)

from typing import (
    Any,
    Literal,
)

from pydantic import (
    BaseModel,
    ConfigDict,
)


class GethKwargs(BaseModel):
    """
    A model for the geth_kwargs parameter of the Geth class.

    Attributes
    ----------
        autodag (bool): generate a DAG (pre-merge only)
        allowinsecure (bool): Allow insecure accounts.
        data_dir (str): The directory to store the chain data.
        etherbase (str): The account to send mining rewards to.
        extradata (str): Extra data to include in the block.
        gasprice (int): Minimum gas price for mining.
        genesis (str): The genesis file to use.
        geth_executable: (str) The path to the geth executable
        ipcdisable (bool): Disable the IPC-RPC server.
        max_peers (str): Maximum number of network peers.
        metrics (bool): Enable metrics collection.
        mine (bool): Enable mining.
        miner_threads (int): Number of CPU threads to use for mining.
        network_id (str): The network identifier.
        nodiscover (bool): Disable network discovery.
        password (str): Path to a file that contains a password.
        port (str): The port to listen on.
        pprof (bool): Enable pprof collection.
        rpc (bool): Enable the HTTP-RPC server.
        rpcaddr (str): The HTTP-RPC server listening interface.
        rpc_port (str): The HTTP-RPC server listening port.
        rpcapi (str): The HTTP-RPC server API.
        targetgaslimit (int): Target gas limit for mining.
        unlock (str): Comma separated list of accounts to unlock.
        verbosity (int): Logging verbosity.
        vmodule (str): Logging verbosity module.
        ws_enabled (bool): Enable the WS-RPC server.
        ws_addr (str): The WS-RPC server listening interface.
        ws_api (str): The WS-RPC server API.
        wsport (int): The WS-RPC server listening port.

    """

    allow_insecure_unlock: bool | None = None
    autodag: bool | None = False
    cache: int | None = None
    data_dir: str | None = None
    dev_mode: bool | None = None
    etherbase: str | None = None
    extradata: str | None = None
    gasprice: int | None = None
    gcmode: Literal["full", "archive"] | None = None
    genesis: str | None = None
    ipc_api: str | None = None  # deprecated
    ipc_disable: bool | None = None
    ipc_path: str | None = None
    max_peers: str | None = None
    metrics: bool | None = None
    mine: bool | None = False
    miner_threads: int | None = None  # deprecated
    miner_etherbase: int | None = None
    network_id: str | None = None
    no_discover: bool | None = None
    password: str | None = None
    preload: str | None = None
    port: str | None = None
    pprof: bool | None = None
    rpc_enabled: bool | None = None
    rpc_addr: str | None = None
    rpc_port: str | None = None
    rpc_api: str | None = None
    rpc_cors_domain: str | None = None
    shh: bool | None = None
    targetgaslimit: int | None = None
    tx_pool_global_slots: int | None = None
    tx_pool_price_limit: int | None = None
    unlock: str | None = None
    verbosity: int | None = None
    vmodule: str | None = None
    ws_enabled: bool | None = None
    ws_addr: str | None = None
    ws_api: str | None = None
    ws_origins: str | None = None
    ws_port: int | None = None
    model_config = ConfigDict(extra="forbid")

    geth_executable: str | None = None
    nice: bool | None = True
    suffix_args: list[str] | None = None
    suffix_kwargs: dict[str, Any] | None = None
    stdin: str | None = None

    def set_field_if_none(self, field_name: str, value: Any) -> None:
        if getattr(self, field_name, None) is None:
            setattr(self, field_name, value)


def validate_geth_kwargs(geth_kwargs: dict[str, Any]) -> bool:
    """
    Converts geth_kwargs to GethKwargs and raises a ValueError if the conversion fails.
    """
    try:
        GethKwargs(**geth_kwargs)
    except TypeError:
        # TODO more specific error message
        raise ValueError("Invalid geth_kwargs")
    return True
