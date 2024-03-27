import os
import sys
from typing import (
    Optional,
)

MAGIC_PREFIX = b"\xfe\xca\xdd\xba\xad\xde\xe1\xfe"  # 0xfee1deadbaddcafe


def get_dag_file_path(
    revision: int = 23,
    seedhash: str = "0000000000000000",
    base_dir: Optional[str] = None,
) -> str:
    if seedhash != "0000000000000000":
        raise NotImplementedError("Non-zero seedhashes are not supported")

    if base_dir is None:
        if sys.platform in {"darwin", "linux", "linux2", "linux3"}:
            base_dir = os.path.expanduser(os.path.join("~", ".ethash"))
        elif sys.platform in {"win32", "cygwin"}:
            base_dir = os.path.expanduser(
                os.path.join(
                    "~",
                    "Appdata",
                    "Local",
                    "Ethash",
                )
            )
        else:
            raise ValueError(f"Unknown platform: {sys.platform}")

    dag_filename = f"full-R{revision}-{seedhash}"

    dag_file_path = os.path.join(base_dir, dag_filename)
    return dag_file_path


def get_magic_bytes(dag_file_path: str) -> bytes:
    with open(dag_file_path, "rb") as dag_file:
        return dag_file.read(8)


def is_dag_generated(
    revision: int = 23,
    seedhash: str = "0000000000000000",
    base_dir: Optional[str] = None,
) -> bool:
    dag_file_path = get_dag_file_path(revision, seedhash, base_dir)

    if not os.path.exists(dag_file_path):
        return False

    dag_file_prefix = get_magic_bytes(dag_file_path)

    return dag_file_prefix == MAGIC_PREFIX
