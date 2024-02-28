from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
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

    allow_insecure_unlock: Optional[bool] = None
    autodag: Optional[bool] = False
    cache: Optional[int] = None
    data_dir: Optional[str] = None
    etherbase: Optional[str] = None
    extradata: Optional[str] = None
    gasprice: Optional[int] = None
    gcmode: Optional[Literal["full", "archive"]] = None
    genesis: Optional[str] = None
    ipc_api: Optional[str] = None  # deprecated
    ipc_disable: Optional[bool] = None
    ipc_path: Optional[str] = None
    max_peers: Optional[str] = None
    metrics: Optional[bool] = None
    mine: Optional[bool] = False
    miner_threads: Optional[int] = None  # deprecated
    miner_etherbase: Optional[int] = None
    network_id: Optional[str] = None
    nodiscover: Optional[bool] = None
    password: Optional[str] = None
    preload: Optional[str] = None
    port: Optional[str] = None
    pprof: Optional[bool] = None
    rpc_enabled: Optional[bool] = None
    rpc_addr: Optional[str] = None
    rpc_port: Optional[str] = None
    rpc_api: Optional[str] = None
    rpc_cors_domain: Optional[str] = None
    shh: Optional[bool] = None
    targetgaslimit: Optional[int] = None
    tx_pool_global_slots: Optional[int] = None
    tx_pool_price_limit: Optional[int] = None
    unlock: Optional[str] = None
    verbosity: Optional[int] = None
    vmodule: Optional[str] = None
    ws_enabled: Optional[bool] = None
    ws_addr: Optional[str] = None
    ws_api: Optional[str] = None
    ws_origins: Optional[str] = None
    ws_port: Optional[int] = None
    model_config = ConfigDict(extra="forbid")

    geth_executable: Optional[str] = None
    nice: Optional[bool] = True
    suffix_args: Optional[List[str]] = None
    suffix_kwargs: Optional[Dict[str, Any]] = None
    stdin: Optional[str] = None

    def set_field_if_none(self, field_name: str, value: Any) -> None:
        if getattr(self, field_name, None) is None:
            setattr(self, field_name, value)


class GenesisData(BaseModel):
    """
    A model for the genesis data.

    Attributes
    ----------
        alloc (dict): The genesis allocation.
        clique (dict): The genesis clique.
        coinbase (str): The genesis coinbase.
        config (dict): The genesis configuration.
        difficulty (int): The genesis difficulty.
        extraData (str): The genesis extra data.
        gasLimit (int): The genesis gas limit.
        mixhash (str): The genesis mix hash.
        nonce (str): The genesis nonce.
        parentHash (str): The genesis parent hash.
        timestamp (str): The genesis timestamp.

    """

    alloc: Optional[Dict[bytes, Dict[str, Any]]] = None
    clique: Optional[Dict[str, int]] = None
    coinbase: bytes = b"0x3333333333333333333333333333333333333333"
    config: Optional[Dict[str, Any]] = None
    difficulty: str = "0x01"
    extraData: Optional[str] = None
    gasLimit: str = "0x47d5cc"
    mixhash: str = "0x0000000000000000000000000000000000000000000000000000000000000000"
    nonce: str = "0xdeadbeefdeadbeef"
    overwrite: bool = False
    parentHash: str = "0x0000000000000000000000000000000000000000000000000000000000000000"  # noqa: E501
    timestamp: str = "0x0"
