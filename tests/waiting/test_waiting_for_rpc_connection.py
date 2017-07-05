import pytest

from flaky import flaky

from geth import DevGethProcess
from geth.utils.compat import (
    Timeout,
)


def test_waiting_for_rpc_connection(base_dir):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        geth.wait_for_rpc(timeout=60)
        assert geth.is_running


@flaky(max_runs=3)
def test_timeout_waiting_for_rpc_connection(base_dir):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        with pytest.raises(Timeout):
            geth.wait_for_rpc(timeout=0.1)
