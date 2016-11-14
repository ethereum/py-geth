from gevent import monkey

def patch():
    """Run in gevent monkey patching.

    required for urllib use.
    """
    monkey.patch_socket()
