from geth import RopstenGethProcess
from geth.mixins import LoggingMixin
from geth.utils.networking import get_open_port


class LoggedRopstenGethProcess(LoggingMixin, RopstenGethProcess):
    pass


def test_testnet_chain_with_no_overrides():
    geth = LoggedRopstenGethProcess(geth_kwargs={'port': get_open_port()})

    geth.start()

    geth.wait_for_ipc(180)

    assert geth.is_running
    assert geth.is_alive

    geth.stop()

    assert geth.is_stopped
