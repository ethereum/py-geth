import codecs
from typing import (
    Any,
    Union,
    cast,
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


def force_bytes(
    value: Union[str, bytes, bytearray], encoding: str = "iso-8859-1"
) -> bytes:
    if is_binary(value):
        binary_value = cast(Union[bytes, bytearray], value)
        return bytes(binary_value)
    elif is_text(value):
        text_value = cast(str, value)
        encoded = codecs.encode(text_value, encoding)
        if is_binary(encoded):
            return encoded
        else:
            raise TypeError(
                f"Encoding {encoding!r} produced non-binary result: {encoded!r}"
            )
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


def force_text(
    value: Union[str, bytes, bytearray], encoding: str = "iso-8859-1"
) -> str:
    if is_text(value):
        text_value = cast(str, value)
        return text_value
    elif is_binary(value):
        binary_value = cast(Union[bytes, bytearray], value)
        return codecs.decode(binary_value, encoding)
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
