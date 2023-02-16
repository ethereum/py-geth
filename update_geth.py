"""
This script is meant to automate adding support for new geth versions.

To add support for a geth version, run the following line from the py-geth directory, substituting
the version for the one you wish to add support for. Note that the 'v' in the versioning is
optional.

.. code-block:: shell

    $ python update_geth.py v1.10.9

To introduce support for more than one version, pass in the versions in increasing order,
ending with the latest version.

.. code-block:: shell

    $ python update_geth.py v1.10.7 v1.10.8 v1.10.9

Note: Always review your changes before committing as something may cause this existing pattern to
change at some point.
"""

import fileinput
import re
import sys

GETH_VERSION_REGEX = re.compile(r'v\d*\.\d+')  # v0.0.0 pattern

# get the current go version
go_version = None
with open('.circleci/config.yml') as circleci_config:
    golang_keyword = '&common_go_v_'
    for line in circleci_config:
        if golang_keyword in line:
            go_version = line[line.find(golang_keyword) + len(golang_keyword):].strip()
            break
if go_version is None:
    raise ValueError('go version was not properly parsed from config')

currently_supported_geth_versions = []
with open('tox.ini') as tox_ini:
    for line_number, line in enumerate(tox_ini, start=1):
        if line_number == 15:
            # supported versions are near the beginning of the tox.ini file
            break
        if 'install-geth' in line:
            line.replace(' ', '')
            circleci_python_versions = line[line.find('py{')+3: line.find('}')].split(',')
        if GETH_VERSION_REGEX.search(line):
            line = line.replace(' ', '')  # clean space
            line = line.replace('\n', '')  # remove trailing indent
            line = line.replace('\\', '')  # remove the multiline backslash
            line = line if line[-1] != ',' else line[:-1]
            for version in line.split(','):
                currently_supported_geth_versions.append(version.strip())
LATEST_SUPPORTED_GETH_VERSION = currently_supported_geth_versions[-1]
LATEST_PYTHON_VERSION = circleci_python_versions[-1]

# .circleci/config.yml pattern
CIRCLE_CI_PATTERN = {
    'jobs': '',
    'workflow_test_jobs': '',
}
# geth/install.py pattern
GETH_INSTALL_PATTERN = {
    'versions': '',
    'installs': '',
    'version<->install': '',
}

user_provided_versions = sys.argv[1:]
normalized_user_versions = []
for index, user_provided_version in enumerate(user_provided_versions):
    if 'v' not in user_provided_version:
        user_provided_version = f'v{user_provided_version}'
    normalized_user_versions.append(user_provided_version)

    if not GETH_VERSION_REGEX.match(user_provided_version) or len(user_provided_versions) == 0:
        raise ValueError('missing or improper format for provided geth versions')

    if user_provided_version in currently_supported_geth_versions:
        raise ValueError(
            f'provided version is already supported: {user_provided_version}'
        )
    latest_user_provided_version = normalized_user_versions[-1]

    # set up .circleci/config.yml pattern
    if index > 0:
        CIRCLE_CI_PATTERN['workflow_test_jobs'] += '\n'

    for py_version in circleci_python_versions:
        py_version_decimal = f'{py_version[0]}.{py_version[1:]}'
        CIRCLE_CI_PATTERN['jobs'] += (
            f"  py{py_version}-install-geth-{user_provided_version}:\n"
            f"    <<: *common_go_v_{go_version}\n"
            "    docker:\n"
            f"      - image: cimg/python:{py_version_decimal}\n"
            "        environment:\n"
            f"          GETH_VERSION: {user_provided_version}\n"
            f"          TOXENV: py{py_version}-install-geth-{user_provided_version}\n"
        )

        CIRCLE_CI_PATTERN['workflow_test_jobs'] += (
            f"\n      - py{py_version}-install-geth-{user_provided_version}"
        )

    # set up geth/install.py pattern
    user_version_upper_underscored = user_provided_version.replace('.', '_').upper()
    GETH_INSTALL_PATTERN['versions'] += (
        f"{user_version_upper_underscored} = '{user_provided_version}'\n"
    )

    user_version_install = f'install_v{user_version_upper_underscored[1:]}'
    GETH_INSTALL_PATTERN['installs'] += (
        f'{user_version_install} = functools.partial('
        f'install_from_source_code_release, {user_version_upper_underscored})\n'
    )
    GETH_INSTALL_PATTERN['version<->install'] += (
        f'        {user_version_upper_underscored}: {user_version_install},\n'
    )

# update .circleci/config.yml versions
with fileinput.FileInput('.circleci/config.yml', inplace=True) as cci_config:
    for line in cci_config:
        if (
            f"TOXENV: py{LATEST_PYTHON_VERSION}-install-geth-{LATEST_SUPPORTED_GETH_VERSION}"
        ) in line:
            print(
                f"          TOXENV: py{LATEST_PYTHON_VERSION}-install-geth-"
                f"{LATEST_SUPPORTED_GETH_VERSION}\n" + CIRCLE_CI_PATTERN['jobs'], end=''
            )
        elif (
            f"- py{LATEST_PYTHON_VERSION}-install-geth-{LATEST_SUPPORTED_GETH_VERSION}"
        ) in line:
            print(
                f"      - py{LATEST_PYTHON_VERSION}-install-geth-{LATEST_SUPPORTED_GETH_VERSION}\n"
                + CIRCLE_CI_PATTERN['workflow_test_jobs']
            )
        else:
            print(line, end='')

# update geth/install.py versions
with fileinput.FileInput('geth/install.py', inplace=True) as geth_install:
    latest_version_upper_underscored = LATEST_SUPPORTED_GETH_VERSION.upper().replace('.', '_')
    latest_version_install = f'install_v{latest_version_upper_underscored[1:]}'
    for line in geth_install:
        if f"{latest_version_upper_underscored} = '{LATEST_SUPPORTED_GETH_VERSION}'" in line:
            print(
                f"{latest_version_upper_underscored} = '{LATEST_SUPPORTED_GETH_VERSION}'\n"
                + GETH_INSTALL_PATTERN['versions'], end='')
        elif f"{latest_version_install} = functools.partial" in line:
            print(
                f'{latest_version_install} = functools.partial('
                f'install_from_source_code_release, {latest_version_upper_underscored})\n'
                + GETH_INSTALL_PATTERN['installs'], end=''
            )
        elif (
            f"{latest_version_upper_underscored}: {latest_version_install}"
        ) in line:
            print(
                f'        {latest_version_upper_underscored}: {latest_version_install},\n'
                + GETH_INSTALL_PATTERN['version<->install'], end=''
            )
        else:
            print(line, end='')

# update versions in readme to the latest supported version
with fileinput.FileInput('README.md', inplace=True) as readme:
    latest_version_upper_underscored = LATEST_SUPPORTED_GETH_VERSION.upper().replace('.', '_')
    for line in readme:
        print(line.replace(LATEST_SUPPORTED_GETH_VERSION, latest_user_provided_version), end='')

# update tox.ini versions
with fileinput.FileInput('tox.ini', inplace=True) as tox_ini:
    all_versions = currently_supported_geth_versions + normalized_user_versions
    write_versions = False
    for line in tox_ini:
        if write_versions:
            print('        ', end='')
            for num, v in enumerate(all_versions, start=1):
                if num == len(all_versions):
                    print(f'{v} \\')
                elif not num % 7:
                    print(f'{v}, \\\n        ', end='')
                else:
                    print(v, end=', ')
            write_versions = False
        else:
            if 'install-geth-{' in line:
                write_versions = True
            if GETH_VERSION_REGEX.search(line):
                # clean up the older version lines
                print(end='')
            else:
                print(line, end='')
