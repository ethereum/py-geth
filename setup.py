#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)


setup(
    name='py-geth',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='1.13.0',
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
    extras_require={
        'gevent': [
            "gevent>=1.1.1,!=1.2.0",
        ],
    },
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
