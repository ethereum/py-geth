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
        geth_executable: (str) The path to the geth executable
        ipcdisable (bool): Disable the IPC-RPC server.
        max_peers (str): Maximum number of network peers.
        mine (bool): Enable mining.
        network_id (str): The network identifier.
        nodiscover (bool): Disable network discovery.
        password (str): Path to a file that contains a password.
        port (str): The port to listen on.
        rpc (bool): Enable the HTTP-RPC server.
        rpcaddr (str): The HTTP-RPC server listening interface.
        rpc_port (str): The HTTP-RPC server listening port.
        rpcapi (str): The HTTP-RPC server API.
        unlock (str): Comma separated list of accounts to unlock.
        verbosity (int): Logging verbosity.
        ws_enabled (bool): Enable the WS-RPC server.
        ws_addr (str): The WS-RPC server listening interface.
        ws_api (str): The WS-RPC server API.
        wsport (int): The WS-RPC server listening port.

    """

    allow_insecure_unlock: bool | None = None
    autodag: bool | None = False
    cache: int | None = None
    data_dir: str | None = None
    dev_mode: bool | None = False
    gcmode: Literal["full", "archive"] | None = None
    geth_executable: str | None = None
    ipc_disable: bool | None = None
    ipc_path: str | None = None
    max_peers: str | None = None
    mine: bool | None = False
    miner_etherbase: int | None = None
    network_id: str | None = None
    nice: bool | None = True
    no_discover: bool | None = None
    password: str | None = None
    port: str | None = None
    preload: str | None = None
    rpc_addr: str | None = None
    rpc_api: str | None = None
    rpc_cors_domain: str | None = None
    rpc_enabled: bool | None = None
    rpc_port: str | None = None
    shh: bool | None = None
    stdin: str | None = None
    suffix_args: list[str] | None = None
    suffix_kwargs: dict[str, Any] | None = None
    tx_pool_global_slots: int | None = None
    tx_pool_price_limit: int | None = None
    unlock: str | None = None
    verbosity: int | None = None
    ws_addr: str | None = None
    ws_api: str | None = None
    ws_enabled: bool | None = None
    ws_origins: str | None = None
    ws_port: int | None = None

    model_config = ConfigDict(extra="forbid")

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
