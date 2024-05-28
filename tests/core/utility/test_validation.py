from __future__ import (
    annotations,
)

import sys
from typing import (
    get_type_hints,
)

import pytest

from geth.utils.validation import (
    GenesisData,
    GenesisDataTypedDict,
    validate_genesis_data,
    validate_geth_kwargs,
)


def test_validate_geth_kwargs_good():
    geth_kwargs = {
        "data_dir": "/tmp",
        "network_id": "123",
        "rpc_port": "1234",
        "dev_mode": True,
    }

    assert validate_geth_kwargs(geth_kwargs) is True


def test_validate_geth_kwargs_bad():
    geth_kwargs = {
        "data_dir": "/tmp",
        "network_id": 123,
        "dev_mode": "abc",
    }

    with pytest.raises(ValueError):
        validate_geth_kwargs(geth_kwargs)


def test_validate_genesis_data_good():
    genesis_data = {
        "difficulty": "0x00012131",
        "nonce": "abc",
        "timestamp": "1234",
    }

    assert validate_genesis_data(genesis_data) is True


def test_validate_genesis_data_bad():
    genesis_data = {
        "difficulty": "0x00012131",
        "nonce": "abc",
        "cats": "1234",
    }

    with pytest.raises(ValueError):
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
