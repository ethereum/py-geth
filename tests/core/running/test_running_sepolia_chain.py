from geth import (
    SepoliaGethProcess,
)
from geth.mixins import (
    LoggingMixin,
)
from geth.utils.networking import (
    get_open_port,
)


class LoggedSepoliaGethProcess(LoggingMixin, SepoliaGethProcess):
    pass


def test_testnet_chain_with_no_overrides():
    geth = LoggedSepoliaGethProcess(geth_kwargs={"port": get_open_port()})

    geth.start()

    geth.wait_for_ipc(180)

    assert geth.is_running
    assert geth.is_alive

    geth.stop()

    assert geth.is_stopped
