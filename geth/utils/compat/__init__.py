import os


def get_threading_backend():
    if 'GETH_THREADING_BACKEND' in os.environ:
        return os.environ['GETH_THREADING_BACKEND']
    elif 'THREADING_BACKEND' in os.environ:
        return os.environ['THREADING_BACKEND']
    else:
        return 'stdlib'


THREADING_BACKEND = get_threading_backend()


if THREADING_BACKEND == 'stdlib':
    from .compat_stdlib import (  # noqa
        Timeout,
        spawn,
        sleep,
        subprocess,
        socket,
        JoinableQueue,
    )
elif THREADING_BACKEND == 'gevent':
    from .compat_gevent import (  # noqa
        Timeout,
        spawn,
        sleep,
        subprocess,
        socket,
        JoinableQueue,
    )
else:
    raise ValueError("Unsupported threading backend.  Must be one of 'gevent' or 'stdlib'")
