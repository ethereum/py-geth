from __future__ import (
    annotations,
)

import sys
from typing import (
    get_type_hints,
)

import pytest

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GenesisDataTypedDict,
)
from geth.utils.validation import (
    GenesisData,
    fill_default_genesis_data,
    validate_genesis_data,
    validate_geth_kwargs,
)


@pytest.mark.parametrize(
    "geth_kwargs",
    [
        {
            "data_dir": "/tmp",
            "network_id": "123",
            "rpc_port": "1234",
            "dev_mode": True,
        },
    ],
)
def test_validate_geth_kwargs_good(geth_kwargs):
    assert validate_geth_kwargs(geth_kwargs) is None


@pytest.mark.parametrize(
    "geth_kwargs",
    [
        {
            "data_dir": "/tmp",
            "network_id": 123,
            "dev_mode": "abc",
        }
    ],
)
def test_validate_geth_kwargs_bad(geth_kwargs):
    with pytest.raises(PyGethValueError):
        validate_geth_kwargs(geth_kwargs)


@pytest.mark.parametrize(
    "genesis_data",
    [
        {
            "difficulty": "0x00012131",
            "nonce": "abc",
            "timestamp": "1234",
        }
    ],
)
def test_validate_genesis_data_good(genesis_data):
    assert validate_genesis_data(genesis_data) is None


@pytest.mark.parametrize(
    "genesis_data",
    [
        {
            "difficulty": "0x00012131",
            "nonce": "abc",
            "cats": "1234",
        },
        {
            "difficulty": "0x00012131",
            "nonce": "abc",
            "config": "1234",
        },
        {
            "difficulty": "0x00012131",
            "nonce": "abc",
            "config": None,
        },
        "kangaroo",
    ],
)
def test_validate_genesis_data_bad(genesis_data):
    with pytest.raises(PyGethValueError):
        validate_genesis_data(genesis_data)


@pytest.mark.parametrize(
    "genesis_data,expected",
    [
        (
            {
                "difficulty": "0x00012131",
                "nonce": "abc",
                "timestamp": "1234",
            },
            {
                "alloc": {},
                "baseFeePerGas": "0x0",
                "blobGasUsed": "0x0",
                "coinbase": "0x3333333333333333333333333333333333333333",
                "config": {
                    "chainId": 0,
                    "ethash": {},
                    "homesteadBlock": 0,
                    "daoForkBlock": 0,
                    "daoForkSupport": True,
                    "eip150Block": 0,
                    "eip155Block": 0,
                    "eip158Block": 0,
                    "byzantiumBlock": 0,
                    "constantinopleBlock": 0,
                    "petersburgBlock": 0,
                    "istanbulBlock": 0,
                    "berlinBlock": 0,
                    "londonBlock": 0,
                    "arrowGlacierBlock": 0,
                    "grayGlacierBlock": 0,
                    "terminalTotalDifficulty": 0,
                    "terminalTotalDifficultyPassed": True,
                    "shanghaiTime": 0,
                    "cancunTime": 0,
                },
                "difficulty": "0x00012131",
                "excessBlobGas": "0x0",
                "extraData": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "gasLimit": "0x47e7c4",
                "gasUsed": "0x0",
                "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "nonce": "abc",
                "number": "0x0",
                "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "timestamp": "1234",
            },
        ),
        (
            {
                "difficulty": "0x00012131",
                "nonce": "abc",
                "config": {
                    "homesteadBlock": 5,
                    "daoForkBlock": 1,
                    "daoForkSupport": False,
                    "eip150Block": 27777777,
                    "eip155Block": 99,
                    "eip158Block": 32,
                },
            },
            {
                "alloc": {},
                "baseFeePerGas": "0x0",
                "blobGasUsed": "0x0",
                "coinbase": "0x3333333333333333333333333333333333333333",
                "config": {
                    "chainId": 0,
                    "ethash": {},
                    "homesteadBlock": 5,
                    "daoForkBlock": 1,
                    "daoForkSupport": False,
                    "eip150Block": 27777777,
                    "eip155Block": 99,
                    "eip158Block": 32,
                    "byzantiumBlock": 0,
                    "constantinopleBlock": 0,
                    "petersburgBlock": 0,
                    "istanbulBlock": 0,
                    "berlinBlock": 0,
                    "londonBlock": 0,
                    "arrowGlacierBlock": 0,
                    "grayGlacierBlock": 0,
                    "terminalTotalDifficulty": 0,
                    "terminalTotalDifficultyPassed": True,
                    "shanghaiTime": 0,
                    "cancunTime": 0,
                },
                "difficulty": "0x00012131",
                "excessBlobGas": "0x0",
                "extraData": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "gasLimit": "0x47e7c4",
                "gasUsed": "0x0",
                "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "nonce": "abc",
                "number": "0x0",
                "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "timestamp": "0x0",
            },
        ),
    ],
)
def test_fill_default_genesis_data_good(genesis_data, expected):
    genesis_data_td = GenesisDataTypedDict(**genesis_data)
    filled_genesis_data = fill_default_genesis_data(genesis_data_td).model_dump()
    assert filled_genesis_data == expected


@pytest.mark.parametrize(
    "genesis_data,expected_exception,expected_message",
    [
        (
            {
                "difficulty": "0x00012131",
                "nonce": "abc",
                "timestamp": 1234,
            },
            PyGethValueError,
            "genesis_data validation failed while filling defaults: ",
        ),
        (
            {
                "difficulty": "0x00012131",
                "nonce": "abc",
                "config": {
                    "homesteadBlock": 5,
                    "daoForkBlock": "beep",
                    "daoForkSupport": False,
                    "eip150Block": 27777777,
                    "eip155Block": 99,
                    "eip158Block": 32,
                },
            },
            PyGethValueError,
            "genesis_data validation failed while filling config defaults: ",
        ),
        (
            "abc123",
            PyGethValueError,
            "error while filling default genesis_data: ",
        ),
        (
            {"difficulty": "0x00012131", "nonce": "abc", "config": ["beep"]},
            PyGethValueError,
            "genesis_data validation failed while filling defaults: ",
        ),
    ],
)
def test_fill_default_genesis_data_bad(
    genesis_data, expected_exception, expected_message
):
    with pytest.raises(expected_exception) as excinfo:
        fill_default_genesis_data(genesis_data)
    assert str(excinfo.value).startswith(expected_message)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="get_type_hints requires >=py39")
@pytest.mark.parametrize(
    "model, typed_dict",
    [
        (GenesisData, GenesisDataTypedDict),
    ],
)
def test_model_fields_match_typed_dict(model, typed_dict):
    # Get the fields and types from the Pydantic model
    model_fields = get_type_hints(model)
    assert len(model_fields) > 0, "Model has no fields"

    # Get the fields and types from the TypedDict
    typed_dict_fields = get_type_hints(typed_dict)
    assert len(typed_dict_fields) > 0, "TypedDict has no fields"
    assert len(typed_dict_fields) == len(model_fields), "Field counts do not match"

    # Verify that the fields match
    assert model_fields == typed_dict_fields, "Fields do not match"
