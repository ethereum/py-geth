from geth import (
    MainnetGethProcess,
)
from geth.mixins import (
    LoggingMixin,
)
from geth.utils.networking import (
    get_open_port,
)


class LoggedMainnetGethProcess(LoggingMixin, MainnetGethProcess):
    pass


def test_live_chain_with_no_overrides():
    geth = LoggedMainnetGethProcess(geth_kwargs={"port": get_open_port()})

    geth.start()

    geth.wait_for_ipc(180)

    assert geth.is_running
    assert geth.is_alive

    geth.stop()

    assert geth.is_stopped
