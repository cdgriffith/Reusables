#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import re

# Fix for issues with nosetests, experienced on win7
import multiprocessing

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, "reusables", "__init__.py"), "r") as reuse_file:
    reuse_content = reuse_file.read()

attrs = dict(re.findall(r"__([a-z]+)__ *= *['\"](.+)['\"]", reuse_content))

with open("README.rst", "r") as readme_file:
    long_description = readme_file.read()

packages = ["reusables", "test"]

setup(
    name="reusables",
    version=attrs["version"],
    url="https://github.com/cdgriffith/Reusables",
    license="MIT",
    author=attrs["author"],
    tests_require=["pytest", "coverage >= 3.6", "argparse", "rarfile", "tox", "scandir", "pytest-cov"],
    install_requires=[],
    author_email="chris@cdgriffith.com",
    description="Commonly Consumed Code Commodities",
    long_description=long_description,
    packages=packages,
    include_package_data=True,
    platforms="any",
    setup_requires=["pytest-runner"],
    python_requires='>3.6',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Documentation :: Sphinx",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Compression",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Logging",
    ],
    extras_require={"testing": ["pytest", "coverage >= 3.6", "argparse", "rarfile", "tox", "scandir", "pytest-cov"],},
)
