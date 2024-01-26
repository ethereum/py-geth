#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    "test": [
        "pytest>=7.0.0",
        "pytest-xdist>=2.4.0",
        "flaky>=3.2.0",
    ],
    "lint": [
        "flake8==5.0.4",  # flake8 claims semver but adds new warnings at minor releases, leave it pinned.
        "flake8-bugbear==23.3.12",  # flake8-bugbear does not follow semver, leave it pinned.
        "isort>=5.10.1",
        "black>=23",
        "importlib-metadata<5;python_version<'3.8'",
    ],
    "docs": [
        "towncrier>=21,<22",
    ],
    "dev": [
        "bumpversion>=0.5.3",
        "pytest-watch>=4.1.0",
        "tox>=3.28.0",
        "build>=0.9.0",
        "wheel",
        "twine",
        "ipython",
        "requests>=2.20",
    ],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]
    + extras_require["lint"]
    + extras_require["docs"]
)


with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="py-geth",
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version="3.14.0",
    description="""py-geth: Run Go-Ethereum as a subprocess""",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="The Ethereum Foundation",
    author_email="snakecharmers@ethereum.org",
    url="https://github.com/ethereum/py-geth",
    include_package_data=True,
    py_modules=["geth"],
    install_requires=[
        "semantic-version>=2.6.0",
    ],
    python_requires=">=3.7, <4",
    extras_require=extras_require,
    license="MIT",
    zip_safe=False,
    keywords="ethereum go-ethereum geth",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
