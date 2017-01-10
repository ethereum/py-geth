import os


def is_using_gevent():
    return 'GETH_ASYNC_GEVENT' in os.environ


if is_using_gevent():
    from .gevent_async import (  # noqa
        Timeout,
        sleep,
        subprocess,
        socket,
        JoinableQueue,
    )
else:
    from .stdlib_async import (  # noqa
        Timeout,
        sleep,
        subprocess,
        socket,
        JoinableQueue,
    )
