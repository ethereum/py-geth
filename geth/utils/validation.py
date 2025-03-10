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
    ValidationError,
    model_validator,
)

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GenesisDataTypedDict,
    GethKwargsTypedDict,
)


class GethKwargs(BaseModel):
    cache: str | None = None
    data_dir: str | None = None
    dev_mode: bool | None = False
    dev_period: str | None = None
    gcmode: Literal["full", "archive"] | None = None
    geth_executable: str | None = None
    ipc_disable: bool | None = None
    ipc_path: str | None = None
    max_peers: str | None = None
    network_id: str | None = None
    nice: bool | None = True
    no_discover: bool | None = None
    password: bytes | str | None = None
    port: str | None = None
    preload: str | None = None
    rpc_addr: str | None = None
    rpc_api: str | None = None
    rpc_cors_domain: str | None = None
    rpc_enabled: bool | None = None
    rpc_port: str | None = None
    stdin: str | None = None
    suffix_args: list[str] | None = None
    suffix_kwargs: dict[str, str] | None = None
    tx_pool_global_slots: str | None = None
    tx_pool_lifetime: str | None = None
    tx_pool_price_limit: str | None = None
    verbosity: str | None = None
    ws_addr: str | None = None
    ws_api: str | None = None
    ws_enabled: bool | None = None
    ws_origins: str | None = None
    ws_port: str | None = None

    model_config = ConfigDict(extra="forbid")


def validate_geth_kwargs(geth_kwargs: GethKwargsTypedDict) -> None:
    """
    Converts geth_kwargs to GethKwargs and raises a ValueError if the conversion fails.
    """
    try:
        GethKwargs(**geth_kwargs)
    except ValidationError as e:
        raise PyGethValueError(f"geth_kwargs validation failed: {e}")
    except TypeError as e:
        raise PyGethValueError(f"error while validating geth_kwargs: {e}")


class GenesisDataConfig(BaseModel):
    """
    Default values are pulled from the ``genesis.json`` file internal to the repository.
    """

    chainId: int | None = None
    ethash: dict[str, Any] | None = None
    homesteadBlock: int | None = None
    daoForkBlock: int | None = None
    daoForkSupport: bool | None = None
    eip150Block: int | None = None
    eip155Block: int | None = None
    eip158Block: int | None = None
    byzantiumBlock: int | None = None
    constantinopleBlock: int | None = None
    petersburgBlock: int | None = None
    istanbulBlock: int | None = None
    berlinBlock: int | None = None
    londonBlock: int | None = None
    arrowGlacierBlock: int | None = None
    grayGlacierBlock: int | None = None
    # merge
    terminalTotalDifficulty: int | None = None
    terminalTotalDifficultyPassed: bool | None = None
    # post-merge, timestamp is used for network transitions
    shanghaiTime: int | None = None
    cancunTime: int | None = None
    pragueTime: int | None = None
    # blobs
    blobSchedule: dict[str, Any] = {}

    @model_validator(mode="after")
    def check_blob_schedule_required(
        self,
    ) -> GenesisDataConfig:
        if self.cancunTime and not self.blobSchedule.get("cancun"):
            raise PyGethValueError(
                "blobSchedule 'cancun' value is required when cancunTime is set"
            )
        if self.pragueTime and not self.blobSchedule.get("prague"):
            raise PyGethValueError(
                "blobSchedule 'prague' value is required when pragueTime is set"
            )
        return self


class GenesisData(BaseModel):
    alloc: dict[str, dict[str, Any]] = {}
    baseFeePerGas: str | None = None
    blobGasUsed: str | None = None
    coinbase: str | None = None
    config: dict[str, Any] = GenesisDataConfig().model_dump()
    difficulty: str | None = None
    excessBlobGas: str | None = None
    extraData: str | None = None
    gasLimit: str | None = None
    gasUsed: str | None = None
    mixHash: str | None = None
    nonce: str | None = None
    number: str | None = None
    parentHash: str | None = None
    timestamp: str | None = None

    model_config = ConfigDict(extra="forbid")


def validate_genesis_data(genesis_data: GenesisDataTypedDict) -> None:
    """
    Validates the genesis data
    """
    try:
        GenesisData(**genesis_data)
    except ValidationError as e:
        raise PyGethValueError(f"genesis_data validation failed: {e}")
    except TypeError as e:
        raise PyGethValueError(f"error while validating genesis_data: {e}")

    """
    Validates the genesis data config field
    """
    genesis_data_config = genesis_data.get("config", None)
    if genesis_data_config:
        try:
            GenesisDataConfig(**genesis_data_config)
        except ValidationError as e:
            raise PyGethValueError(f"genesis_data config field validation failed: {e}")
        except TypeError as e:
            raise PyGethValueError(
                f"error while validating genesis_data config field: {e}"
            )
