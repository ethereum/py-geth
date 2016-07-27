import gevent

from pygeth.geth import DevGethProcess
from pygeth.mixins import LoggingMixin


class WithLogging(LoggingMixin, DevGethProcess):
    pass


def wait_for_line(stream, timeout=30):
    with gevent.Timeout(timeout):
        while True:
            line = stream.readline()
            if line:
                break
            gevent.sleep(0.1)


def test_with_logging(base_dir):
    geth = WithLogging('testing', base_dir=base_dir)

    geth.start()

    assert geth.is_running
    assert geth.is_alive

    geth.stop()
