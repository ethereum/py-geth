import pytest

from flaky import flaky

from geth import (
    DevGethProcess,
    get_geth_version
)
from geth.utils.timeout import (
    Timeout,
)


def test_waiting_for_rpc_connection(base_dir):
    version = get_geth_version()

    if version.major == 1:
        if version.minor == 9:
            with DevGethProcess('testing',
                                base_dir=base_dir,
                                overrides={'allow_insecure_unlock': True}) as geth:
                assert geth.is_running
                geth.wait_for_rpc(timeout=60)
        elif version.minor == 7 or version.minor == 8:
            with DevGethProcess('testing',
                                base_dir=base_dir) as geth:
                assert geth.is_running
                geth.wait_for_rpc(timeout=60)
    else:
        assert False, "Unsupported geth version"


@flaky(max_runs=3)
def test_timeout_waiting_for_rpc_connection(base_dir):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        with pytest.raises(Timeout):
            geth.wait_for_rpc(timeout=0.1)
