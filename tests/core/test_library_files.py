import os

from geth.exceptions import (
    GethError,
)

PY_GETH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "geth"
)
DEFAULT_EXCEPTIONS = (
    AssertionError,
    AttributeError,
    FileNotFoundError,
    GethError,
    KeyError,
    NotImplementedError,
    OSError,
    TypeError,
    ValueError,
)


def test_no_default_exceptions_are_raised_within_py_geth():
    for root, _dirs, files in os.walk(PY_GETH_PATH):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        for exception in DEFAULT_EXCEPTIONS:
                            exception_name = exception.__name__
                            if f"raise {exception_name}" in line:
                                raise Exception(
                                    f"``{exception_name}`` raised in py-geth file "
                                    f"``{file}``, line {idx + 1}. "
                                    f"Replace with ``PyGeth{exception_name}``:\n"
                                    f"    file_path:{file_path}\n"
                                    f"    line:{idx + 1}"
                                )
