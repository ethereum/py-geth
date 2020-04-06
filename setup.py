#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)


deps = {
    'test': [
        "pytest>=3.6,<3.7",
        "flaky==3.2.0",
    ],
    'lint': [
        "flake8==3.5.0",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "wheel",
        "setuptools>=36.2.0",
        # Fixing this dependency due to: pytest 3.6.4 has requirement pluggy<0.8,>=0.5, but you'll have pluggy 0.8.0 which is incompatible.
        "pluggy==0.7.1",
        # Fixing this dependency due to: requests 2.20.1 has requirement idna<2.8,>=2.5, but you'll have idna 2.8 which is incompatible.
        "idna==2.7",
        # idna 2.7 is not supported by requests 2.18
        "requests>=2.20,<3",
        "tox==2.7.0",
        "twine",
    ],
}


deps['dev'] = (
    deps['dev'] +
    deps['test'] +
    deps['lint']
)

setup(
    name='py-geth',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='2.3.0',
    description="""Run Go-Ethereum as a subprocess""",
    long_description_markdown_filename='README.md',
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/ethereum/py-geth',
    include_package_data=True,
    py_modules=['geth'],
    install_requires=[
        "semantic-version>=2.6.0",
    ],
    python_requires=">=3",
    extras_require=deps,
    setup_requires=['setuptools-markdown'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum go-ethereum geth',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
