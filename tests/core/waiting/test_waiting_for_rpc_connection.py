from flaky import (
    flaky,
)
import pytest
import semantic_version

from geth import (
    DevGethProcess,
    get_geth_version,
)
from geth.utils.timeout import (
    Timeout,
)


@pytest.mark.skipif(
    get_geth_version() <= semantic_version.Version("1.13.5"),
    reason="Geth had not yet configured dev mode for merge by v1.13.5.",
)
def test_waiting_for_rpc_connection(base_dir):
    with DevGethProcess("testing", base_dir=base_dir) as geth:
        assert geth.is_running
        geth.wait_for_rpc(timeout=20)


@flaky(max_runs=3)
@pytest.mark.skipif(
    get_geth_version() <= semantic_version.Version("1.13.5"),
    reason="Geth had not yet configured dev mode for merge by v1.13.5.",
)
def test_timeout_waiting_for_rpc_connection(base_dir):
    with DevGethProcess("testing", base_dir=base_dir) as geth:
        with pytest.raises(Timeout):
            geth.wait_for_rpc(timeout=0.1)
