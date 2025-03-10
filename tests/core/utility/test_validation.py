from __future__ import (
    annotations,
)

import pytest

from geth.exceptions import (
    PyGethValueError,
)
from geth.utils.validation import (
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
