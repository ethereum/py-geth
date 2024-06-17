import contextlib
import socket
import time
from typing import (
    Generator,
)

from geth.exceptions import (
    PyGethValueError,
)

from .timeout import (
    Timeout,
)


def is_port_open(port: int) -> bool:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        return False
    else:
        return True
    finally:
        sock.close()


def get_open_port() -> str:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


@contextlib.contextmanager
def get_ipc_socket(
    ipc_path: str, timeout: float = 0.1
) -> Generator[socket.socket, None, None]:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(ipc_path)
    sock.settimeout(timeout)

    yield sock

    sock.close()


def wait_for_http_connection(port: int, timeout: int = 5) -> None:
    with Timeout(timeout) as _timeout:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect(("127.0.0.1", port))
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(0.1)
                _timeout.check()
                continue
            else:
                break
        else:
            raise PyGethValueError(
                "Unable to establish HTTP connection, "
                f"timed out after {timeout} seconds"
            )
