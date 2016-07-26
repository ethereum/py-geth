import pytest

import gevent

from pygeth.geth import DevGethProcess


def test_waiting_for_rpc_connection(base_dir):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        geth.wait_for_rpc(timeout=60)
        assert geth.is_running


def test_timeout_waiting_for_rpc_connection(base_dir):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        with pytest.raises(gevent.Timeout):
            geth.wait_for_rpc(timeout=1)
