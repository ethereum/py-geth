import re
from typing import (
    Optional,
)

import semantic_version

from geth.models import (
    GethKwargs,
)

from .utils.encoding import (
    force_text,
)
from .wrapper import (
    geth_wrapper,
)


def get_geth_version_info_string(geth_kwargs: GethKwargs) -> str:
    if getattr(geth_kwargs, "suffix_args", None):
        raise TypeError(
            "The `get_geth_version` function cannot be called with the "
            "`suffix_args` parameter"
        )
    geth_kwargs.suffix_args = ["version"]
    stdoutdata, stderrdata, command, proc = geth_wrapper(geth_kwargs)
    return str(stdoutdata)


VERSION_REGEX = r"Version: (.*)\n"


def get_geth_version(
    geth_kwargs: Optional[GethKwargs] = None,
) -> semantic_version.Version:
    if geth_kwargs is None:
        geth_kwargs = GethKwargs()
    version_info_string = get_geth_version_info_string(geth_kwargs)
    version_match = re.search(VERSION_REGEX, force_text(version_info_string, "utf8"))
    if not version_match:
        raise ValueError(
            f"Did not match version string in geth output:\n{version_info_string}"
        )
    version_string = version_match.groups()[0]
    return semantic_version.Version(version_string)
