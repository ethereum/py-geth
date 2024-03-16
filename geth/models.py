from typing import (
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
        password (str): Password.
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

    # allowinsecure: Optional[bool] = None
    autodag: Optional[bool] = (False,)
    data_dir: Optional[str] = None
    etherbase: Optional[str] = None
    extradata: Optional[str] = None
    gasprice: Optional[int] = None
    genesis: Optional[str] = None
    geth_executable: Optional[str] = None
    ipcdisable: Optional[bool] = None
    max_peers: Optional[str] = None
    metrics: Optional[bool] = None
    mine: Optional[bool] = False
    miner_threads: Optional[int] = None
    network_id: Optional[str] = None
    nodiscover: Optional[bool] = None
    password: Optional[str] = None
    port: Optional[str] = None
    pprof: Optional[bool] = None
    rpc: Optional[bool] = None
    rpcaddr: Optional[str] = None
    rpc_port: Optional[str] = None
    rpcapi: Optional[str] = None
    targetgaslimit: Optional[int] = None
    unlock: Optional[str] = None
    verbosity: Optional[int] = None
    vmodule: Optional[str] = None
    ws_enabled: Optional[bool] = None
    ws_addr: Optional[str] = None
    ws_api: Optional[str] = None
    wsport: Optional[int] = None
    model_config = ConfigDict(extra="forbid")


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

    alloc: Optional[dict]
    clique: Optional[dict]
    coinbase: Optional[str]
    config: Optional[dict]
    difficulty: Optional[int]
    extraData: Optional[str]
    gasLimit: Optional[int]
    mixhash: Optional[str]
    nonce: Optional[str]
    parentHash: Optional[str]
    timestamp: Optional[str]
