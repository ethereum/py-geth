from __future__ import (
    annotations,
)

from typing import (
    IO,
    Any,
    TypedDict,
    Union,
)

IO_Any = Union[IO[Any], int, None]


class GenesisDataTypedDict(TypedDict, total=False):
    alloc: dict[str, dict[str, Any]]
    coinbase: str
    config: dict[str, Any]
    difficulty: str
    extraData: str
    gasLimit: str
    mixhash: str
    nonce: str
    parentHash: str
    timestamp: str
