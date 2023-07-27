import codecs
from typing import (
    Any,
    Union,
)

binary_types = (bytes, bytearray)
text_types = (str,)
string_types = (bytes, str, bytearray)


def is_binary(value: Any) -> bool:
    return isinstance(value, binary_types)


def is_text(value: Any) -> bool:
    return isinstance(value, text_types)


def is_string(value: Any) -> bool:
    return isinstance(value, string_types)


def force_bytes(value: Any, encoding: str = "iso-8859-1") -> Union[bytes, bytearray]:
    if is_binary(value):
        return bytes(value)
    elif is_text(value):
        encoded = codecs.encode(value, encoding)
        if is_binary(encoded):
            return encoded
        else:
            raise TypeError(
                f"Encoding {encoding!r} produced non-binary result: {encoded!r}"
            )
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


def force_text(value: Any, encoding: str = "iso-8859-1") -> str:
    if is_text(value):
        return value
    elif is_binary(value):
        return codecs.decode(value, encoding)
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


def force_obj_to_text(obj: Any) -> Any:
    if is_string(obj):
        return force_text(obj)
    elif isinstance(obj, dict):
        return {force_obj_to_text(k): force_obj_to_text(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(force_obj_to_text(v) for v in obj)
    else:
        return obj
