from pydantic import (
    BaseModel,
    ConfigDict,
)


class GethKwargs(BaseModel):
    """
    A model for the geth_kwargs parameter of the Geth class.
    """

    allowinsecure: bool
    """
    Allow insecure accounts.
    """
    bootnodes: str
    """
    Comma separated enode URLs for P2P discovery bootstrap.
    """
    datadir: str
    """
    The directory to store the chain data.
    """
    etherbase: str
    """
    The account to send mining rewards to.
    """
    extradata: str
    """
    Extra data to include in the block.
    """
    gasprice: int
    """
    Minimum gas price for mining.
    """
    genesis: str
    """
    The genesis file to use.
    """
    ipcdisable: bool
    """
    Disable the IPC-RPC server.
    """
    max_peers: str
    """
    Maximum number of network peers.
    """
    metrics: bool
    """
    Enable metrics collection.
    """
    mine: bool
    """
    Enable mining.
    """
    minerthreads: int
    """
    Number of CPU threads to use for mining.
    """
    network_id: str
    """
    The network identifier.
    """
    no_discover: bool
    password: str
    """
    Password
    """
    port: str
    """
    The port to listen on.
    """
    pprof: bool
    """
    Enable pprof collection.
    """
    rpc: bool
    """
    Enable the HTTP-RPC server.
    """
    rpcaddr: str
    """
    The HTTP-RPC server listening interface.
    """
    rpc_port: str
    """
    The HTTP-RPC server listening port.
    """
    rpcapi: str
    """
    The HTTP-RPC server API.
    """
    targetgaslimit: int
    """
    Target gas limit for mining.
    """
    unlock: str
    """
    Comma separated list of accounts to unlock.
    """
    verbosity: int
    """
    Logging verbosity.
    """
    vmodule: str
    """
    Logging verbosity module.
    """
    ws_enabled: bool
    """
    Enable the WS-RPC server.
    """
    ws_addr: str
    """
    The WS-RPC server listening interface.
    """
    ws_api: str
    """
    The WS-RPC server API.
    """
    wsport: int
    """
    The WS-RPC server listening port.
    """
    model_config = ConfigDict(extra="error")


class GenesisData(BaseModel):
    """
    A model for the genesis data.
    """

    alloc: dict
    """
    The genesis allocation.
    """
    clique: dict
    """
    The genesis clique.
    """
    coinbase: str
    """
    The genesis coinbase.
    """
    config: dict
    """
    The genesis configuration.
    """
    difficulty: int
    """
    The genesis difficulty.
    """
    extraData: str
    """
    The genesis extra data.
    """
    gasLimit: int
    """
    The genesis gas limit.
    """
    mixhash: str
    """
    The genesis mix hash.
    """
    nonce: str
    """
    The genesis nonce.
    """
    parentHash: str
    """
    The genesis parent hash.
    """
    timestamp: str
    """
    The genesis timestamp.
    """
