import contextlib

from gevent import socket


def is_port_open(port):
    sock = socket.socket()
    try:
        sock.bind(('127.0.0.1', port))
    except socket.error:
        return False
    else:
        sock.close()
        return True


def get_open_port():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


@contextlib.contextmanager
def get_ipc_socket(ipc_path, timeout=0.1):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(ipc_path)
    sock.settimeout(timeout)

    yield sock

    sock.close()
