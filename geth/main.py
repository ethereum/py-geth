from __future__ import (
    annotations,
)

import re

import semantic_version
from typing_extensions import (
    Unpack,
)

from geth.exceptions import (
    PyGethTypeError,
    PyGethValueError,
)
from geth.types import (
    GethKwargsTypedDict,
)
from geth.utils.validation import (
    validate_geth_kwargs,
)

from .utils.encoding import (
    force_text,
)
from .wrapper import (
    geth_wrapper,
)


def get_geth_version_info_string(**geth_kwargs: Unpack[GethKwargsTypedDict]) -> str:
    if "suffix_args" in geth_kwargs:
        raise PyGethTypeError(
            "The `get_geth_version` function cannot be called with the "
            "`suffix_args` parameter"
        )
    geth_kwargs["suffix_args"] = ["version"]
    validate_geth_kwargs(geth_kwargs)
    stdoutdata, stderrdata, command, proc = geth_wrapper(**geth_kwargs)
    return stdoutdata.decode("utf-8")


VERSION_REGEX = r"Version: (.*)\n"


def get_geth_version(
    **geth_kwargs: Unpack[GethKwargsTypedDict],
) -> semantic_version.Version:
    validate_geth_kwargs(geth_kwargs)
    version_info_string = get_geth_version_info_string(**geth_kwargs)
    version_match = re.search(VERSION_REGEX, force_text(version_info_string, "utf8"))
    if not version_match:
        raise PyGethValueError(
            f"Did not match version string in geth output:\n{version_info_string}"
        )
    version_string = version_match.groups()[0]
    return semantic_version.Version(version_string)
