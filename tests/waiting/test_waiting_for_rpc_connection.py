import pytest

import gevent

from pygeth.geth import DevGethProcess
from pygeth.utils.networking import (
    get_open_port,
)


def test_waiting_for_rpc_connection(base_dir):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        geth.wait_for_rpc(timeout=60)
        assert geth.is_running


def test_timeout_waiting_for_rpc_connection(base_dir, monkeypatch):
    with DevGethProcess('testing', base_dir=base_dir) as geth:
        monkeypatch.setattr(geth, 'rpc_port', get_open_port())
        with pytest.raises(gevent.Timeout):
            geth.wait_for_rpc(timeout=1)
