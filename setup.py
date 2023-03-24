#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)


deps = {
    'test': [
        "pytest>=6.2.5,<8",
        "flaky>=3.2.0,<4",
        "pluggy>=0.7.1,<1",
    ],
    'lint': [
        "flake8>=3.9.2,<4",
        "importlib-metadata<5;python_version<'3.8'",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "wheel",
        "setuptools>=38.6.0",
        "requests>=2.20,<3",
        "tox>=2.7.0",
        "twine",
    ],
}


deps['dev'] = (
    deps['dev'] +
    deps['test'] +
    deps['lint']
)

with open('./README.md') as readme:
    long_description = readme.read()

setup(
    name='py-geth',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='3.12.0',
    description="""Run Go-Ethereum as a subprocess""",
    long_description_content_type='text/markdown',
    long_description=long_description,
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
    license="MIT",
    zip_safe=False,
    keywords='ethereum go-ethereum geth',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
