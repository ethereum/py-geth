import pytest

from flaky import flaky

from geth import DevGethProcess, get_geth_version
from geth.utils.timeout import (
    Timeout,
)


def test_waiting_for_rpc_connection(base_dir, _amend_geth_overrides_for_1_9):
    with DevGethProcess(
        "testing", base_dir=base_dir, overrides=_amend_geth_overrides_for_1_9
    ) as geth:
        assert geth.is_running
        geth.wait_for_rpc(timeout=60)


@flaky(max_runs=3)
def test_timeout_waiting_for_rpc_connection(base_dir, _amend_geth_overrides_for_1_9):
    with DevGethProcess(
        "testing", base_dir=base_dir, overrides=_amend_geth_overrides_for_1_9
    ) as geth:
        with pytest.raises(Timeout):
            geth.wait_for_rpc(timeout=0.1)
