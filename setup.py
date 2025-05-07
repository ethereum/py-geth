#!/usr/bin/env python
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    "dev": [
        "build>=0.9.0",
        "bump_my_version>=0.19.0",
        "ipython",
        "mypy==1.10.0",
        "pre-commit>=3.4.0",
        "tox>=4.0.0",
        "twine",
        "wheel",
    ],
    "docs": [
        "towncrier>=24,<25",
    ],
    "test": [
        "flaky>=3.2.0",
        "pytest>=7.0.0",
        "pytest-xdist>=2.4.0",
    ],
}

extras_require["dev"] = (
    extras_require["dev"] + extras_require["docs"] + extras_require["test"]
)


with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="py-geth",
    # *IMPORTANT*: Don't manually change the version here. Use the 'bump-my-version' utility.
    version="5.6.0",
    description="""py-geth: Run Go-Ethereum as a subprocess""",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="The Ethereum Foundation",
    author_email="snakecharmers@ethereum.org",
    url="https://github.com/ethereum/py-geth",
    include_package_data=True,
    py_modules=["geth"],
    install_requires=[
        "eval_type_backport>=0.1.0; python_version < '3.10'",
        "pydantic>=2.6.0",
        "requests>=2.23",
        "semantic-version>=2.6.0",
        "types-requests>=2.0.0",
        "typing-extensions>=4.0.1",
    ],
    python_requires=">=3.8, <4",
    extras_require=extras_require,
    license="MIT",
    zip_safe=False,
    keywords="ethereum go-ethereum geth",
    packages=find_packages(exclude=["scripts", "scripts.*", "tests", "tests.*"]),
    package_data={"geth": ["py.typed"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
