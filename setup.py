#!/usr/bin/env python
#-*- coding: utf-8 -*-
from setuptools import setup
import os

root = os.path.abspath(os.path.dirname(__file__))

with open("requirements.txt", "r") as required:
    requirements = [x.strip() for x in required.readlines() if x.strip()]

with open("requirements-test.txt", "r") as test_required:
    requirements_test = [x.strip() for x in test_required.readlines() if x.strip()]


with open(os.path.join(root, "reuse", "reuse.py"), "r") as reuse_file:
    reuse_content = reuse_file.read()

import re
attrs = dict(re.findall(r"__([a-z]+)__ *= *['\"](.+)['\"]", reuse_content))


with open("README.rst", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name='reuse',
    version=attrs['version'],
    url='https://github.com/cdgriffith/Reusables',
    license='MIT',
    author=attrs['author'],
    tests_require=requirements_test,
    install_requires=requirements,
    author_email='chris@cdgriffith.com',
    description='Commonly Consumed Code Commodities',
    long_description=long_description,
    packages=['reuse'],
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    extras_require={
        'testing': requirements_test,
    }
)