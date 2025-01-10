"""
A script to automate adding support for new geth versions.

To add support for a geth version, run the following line from the py-geth directory,
substituting the version for the one you wish to add support for. Note that the 'v' in
the versioning is optional.

.. code-block:: shell

    $ python update_geth.py v1_10_9

To introduce support for more than one version, pass in the versions in increasing
order, ending with the latest version.

.. code-block:: shell

    $ python update_geth.py v1_10_7 v1_10_8 v1_10_9

Note: Always review your changes before committing as something may cause this existing
pattern to change at some point.
"""

import fileinput
import re
import sys

GETH_VERSION_REGEX = re.compile(r"v\d*_\d+")  # v0_0_0 pattern
GETH_VERSION_REGEX_NO_V = re.compile(r"\d*_\d+")  # 0_0_0 pattern

currently_supported_geth_versions = []
with open("tox.ini") as tox_ini:
    for line_number, line in enumerate(tox_ini, start=1):
        if line_number == 15:
            # supported versions are near the beginning of the tox.ini file
            break
        if "install-geth" in line:
            line.replace(" ", "")
            circleci_python_versions = line[
                line.find("py{") + 3 : line.find("}")
            ].split(",")
        if GETH_VERSION_REGEX.search(line):
            line = line.replace(" ", "")  # clean space
            line = line.replace("\n", "")  # remove trailing indent
            line = line.replace("\\", "")  # remove the multiline backslash
            line = line if line[-1] != "," else line[:-1]
            for version in line.split(","):
                currently_supported_geth_versions.append(version.strip())
LATEST_SUPPORTED_GETH_VERSION = currently_supported_geth_versions[-1]
LATEST_PYTHON_VERSION = circleci_python_versions[-1]

# geth/install.py pattern
GETH_INSTALL_PATTERN = {
    "versions": "",
    "installs": "",
    "version<->install": "",
}

user_provided_versions = sys.argv[1:]
normalized_user_versions = []
for user_provided_version in user_provided_versions:
    if "v" not in user_provided_version:
        user_provided_version = f"v{user_provided_version}"
    normalized_user_versions.append(user_provided_version)

    if (
        not GETH_VERSION_REGEX.match(user_provided_version)
        or len(user_provided_versions) == 0
    ):
        raise ValueError("missing or improper format for provided geth versions")

    if user_provided_version in currently_supported_geth_versions:
        raise ValueError(
            f"provided version is already supported: {user_provided_version}"
        )
    latest_user_provided_version = normalized_user_versions[-1]

    # set up geth/install.py pattern
    user_version_upper = user_provided_version.upper()
    user_version_period = user_provided_version.replace("_", ".")
    GETH_INSTALL_PATTERN[
        "versions"
    ] += f'{user_version_upper} = "{user_version_period}"\n'

    user_version_install = f"install_v{user_version_upper[1:]}"
    GETH_INSTALL_PATTERN["installs"] += (
        f"{user_version_install} = functools.partial("
        f"install_from_source_code_release, {user_version_upper})\n"
    )
    GETH_INSTALL_PATTERN[
        "version<->install"
    ] += f"        {user_version_upper}: {user_version_install},\n"


ALL_VERSIONS = currently_supported_geth_versions + normalized_user_versions

# update .circleci/config.yml versions
with fileinput.FileInput(".circleci/config.yml", inplace=True) as cci_config:
    all_versions_no_v = [version[1:] for version in ALL_VERSIONS]
    in_geth_versions = False
    for line in cci_config:
        if in_geth_versions:
            print("                ", end="")
            for num, v in enumerate(all_versions_no_v, start=1):
                if num == len(all_versions_no_v):
                    print(f'"{v}"', end="\n")
                # at most 6 versions per line
                elif not num % 6:
                    print(f'"{v}",\n                ', end="")
                else:
                    print(f'"{v}"', end=", ")
            in_geth_versions = False
        else:
            if "geth_version: [" in line:
                in_geth_versions = True
            if GETH_VERSION_REGEX_NO_V.search(line):
                # clean up the older version lines
                print(end="")
            else:
                print(line, end="")

# update geth/install.py versions
with fileinput.FileInput("geth/install.py", inplace=True) as geth_install:
    latest_supported_upper = LATEST_SUPPORTED_GETH_VERSION.upper()
    latest_supported_period = LATEST_SUPPORTED_GETH_VERSION.replace("_", ".")
    latest_version_install = f"install_v{latest_supported_upper[1:]}"
    for line in geth_install:
        if f'{latest_supported_upper} = "{latest_supported_period}"' in line:
            print(
                f'{latest_supported_upper} = "{latest_supported_period}"\n'
                + GETH_INSTALL_PATTERN["versions"],
                end="",
            )
        elif f"{latest_version_install} = functools.partial" in line:
            print(
                f"{latest_version_install} = functools.partial("
                f"install_from_source_code_release, {latest_supported_upper})\n"
                + GETH_INSTALL_PATTERN["installs"],
                end="",
            )
        elif (f"{latest_supported_upper}: {latest_version_install}") in line:
            print(
                f"        {latest_supported_upper}: {latest_version_install},\n"
                + GETH_INSTALL_PATTERN["version<->install"],
                end="",
            )
        else:
            print(line, end="")

# update versions in readme to the latest supported version
with fileinput.FileInput("README.md", inplace=True) as readme:
    latest_supported_period = LATEST_SUPPORTED_GETH_VERSION.replace("_", ".")
    latest_user_provided_period = latest_user_provided_version.replace("_", ".")
    for line in readme:
        print(
            line.replace(latest_supported_period, latest_user_provided_period),
            end="",
        )

# update tox.ini versions
with fileinput.FileInput("tox.ini", inplace=True) as tox_ini:
    write_versions = False
    for line in tox_ini:
        if write_versions:
            print("        ", end="")
            for num, v in enumerate(ALL_VERSIONS, start=1):
                if num == len(ALL_VERSIONS):
                    print(f"{v} \\")
                elif not num % 7:
                    print(f"{v}, \\\n        ", end="")
                else:
                    print(v, end=", ")
            write_versions = False
        else:
            if "install-geth-{" in line:
                write_versions = True
            if GETH_VERSION_REGEX.search(line):
                # clean up the older version lines
                print(end="")
            else:
                print(line, end="")
