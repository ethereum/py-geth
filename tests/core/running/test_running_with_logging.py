import pytest
import threading

from geth import DevGethProcess
from geth.mixins import LoggingMixin

_ERRORS = []


@pytest.fixture(autouse=True)
def fail_from_errors_on_other_threads():
    # Set excepthook to catch errors in child threads.
    global _ERRORS
    _ERRORS = []

    def pytest_excepthook(*args, **kwargs):
        global _ERRORS
        _ERRORS.extend(args)

    threading.excepthook = pytest_excepthook

    yield

    if _ERRORS:
        caught_errors_str = ', '.join([str(err) for err in _ERRORS])
        pytest.fail(f'Caught exceptions from other threads:\n{caught_errors_str}')


class WithLogging(LoggingMixin, DevGethProcess):
    pass


def test_with_logging(base_dir):
    geth = WithLogging('testing', base_dir=base_dir)

    geth.start()

    assert geth.is_running
    assert geth.is_alive

    geth.stop()
