import pytest

from geth.utils.validation import (
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
