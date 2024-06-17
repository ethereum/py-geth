from __future__ import (
    annotations,
)

import codecs
from typing import (
    Any,
)

from geth.exceptions import (
    PyGethTypeError,
)


def is_string(value: Any) -> bool:
    return isinstance(value, (bytes, bytearray, str))


def force_bytes(value: bytes | bytearray | str, encoding: str = "iso-8859-1") -> bytes:
    if isinstance(value, bytes):
        return value
    elif isinstance(value, bytearray):
        return bytes(value)
    elif isinstance(value, str):
        encoded = codecs.encode(value, encoding)
        if isinstance(encoded, (bytes, bytearray)):
            return encoded
        else:
            raise PyGethTypeError(
                f"Encoding {encoding!r} produced non-binary result: {encoded!r}"
            )
    else:
        raise PyGethTypeError(
            f"Unsupported type: {type(value)}, expected bytes, bytearray or str"
        )


def force_text(value: bytes | bytearray | str, encoding: str = "iso-8859-1") -> str:
    if isinstance(value, (bytes, bytearray)):
        return codecs.decode(value, encoding)
    elif isinstance(value, str):
        return value
    else:
        raise PyGethTypeError(
            f"Unsupported type: {type(value)}, "
            "expected value to be bytes, bytearray or str"
        )


def force_obj_to_text(obj: Any) -> Any:
    if is_string(obj):
        return force_text(obj)
    elif isinstance(obj, dict):
        return {force_obj_to_text(k): force_obj_to_text(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(force_obj_to_text(v) for v in obj)
    else:
        return obj
