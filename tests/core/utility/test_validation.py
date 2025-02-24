from __future__ import (
    annotations,
)

import pytest
import sys
from typing import (
    get_type_hints,
)

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GenesisDataTypedDict,
)
from geth.utils.validation import (
    GenesisData,
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
        {
            "difficulty": "0x00012131",
            "nonce": "abc",
            "timestamp": "1234",
            "config": {
                "cancunTime": 5,
                "blobSchedule": {},
            },
        },
    ],
)
def test_validate_genesis_data_bad(genesis_data):
    with pytest.raises(PyGethValueError):
        validate_genesis_data(genesis_data)


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
