from gevent import monkey


def patch():
    """Run in gevent monkey patching.

    py-geth library internally relies on gevent.
    We need to monkey patch Python stdlib, so that urllib works with
    gevent and py-geth.
    """
    monkey.patch_socket()
