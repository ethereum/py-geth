import threading
from typing import (
    Any,
)


def spawn(target: Any, *args: Any, **kwargs: Any) -> threading.Thread:
    thread = threading.Thread(
        target=target,
        args=args,
        kwargs=kwargs,
    )
    thread.daemon = True
    thread.start()
    return thread
