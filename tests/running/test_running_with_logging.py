from geth import DevGethProcess
from geth.mixins import LoggingMixin


class WithLogging(LoggingMixin, DevGethProcess):
    pass


def test_with_logging(base_dir):
    geth = WithLogging('testing', base_dir=base_dir)

    geth.start()

    assert geth.is_running
    assert geth.is_alive

    geth.stop()
