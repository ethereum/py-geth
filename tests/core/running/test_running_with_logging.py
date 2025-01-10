import pytest
import threading

from geth import (
    DevGethProcess,
)
from geth.mixins import (
    LoggingMixin,
)

_errors = []


@pytest.fixture(autouse=True)
def fail_from_errors_on_other_threads():
    """
    Causes errors when `LoggingMixin` is improperly implemented.
    Useful for preventing false-positives in logging-based tests.
    """

    def pytest_excepthook(*args, **kwargs):
        _errors.extend(args)

    threading.excepthook = pytest_excepthook

    yield

    if _errors:
        caught_errors_str = ", ".join([str(err) for err in _errors])
        pytest.fail(f"Caught exceptions from other threads:\n{caught_errors_str}")


class WithLogging(LoggingMixin, DevGethProcess):
    pass


def test_with_logging(base_dir, caplog):
    test_stdout_path = f"{base_dir}/testing/stdoutlogs.log"
    test_stderr_path = f"{base_dir}/testing/stderrlogs.log"

    geth = WithLogging(
        "testing",
        base_dir=base_dir,
        stdout_logfile_path=test_stdout_path,
        stderr_logfile_path=test_stderr_path,
    )

    geth.start()

    assert geth.is_running
    assert geth.is_alive

    stdout_logger_info = geth.stdout_callbacks[0]
    stderr_logger_info = geth.stderr_callbacks[0]

    stdout_logger_info("test_out")
    stderr_logger_info("test_err")

    with open(test_stdout_path) as out_log_file:
        line = out_log_file.readline()
        assert line == "test_out\n"

    with open(test_stderr_path) as err_log_file:
        line = err_log_file.readline()
        assert line == "test_err\n"

    geth.stop()
