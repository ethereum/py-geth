from geth.geth import TestnetGethProcess
from geth.mixins import LoggingMixin


class LoggedTestnetGethProcess(LoggingMixin, TestnetGethProcess):
    pass


def test_testnet_chain_with_no_overrides():
    geth = LoggedTestnetGethProcess()

    geth.start()

    geth.wait_for_ipc(30)

    assert geth.is_running
    assert geth.is_alive

    geth.stop()

    assert geth.is_stopped
