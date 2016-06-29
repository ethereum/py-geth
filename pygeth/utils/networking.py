import socket


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
