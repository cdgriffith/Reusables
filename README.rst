Reusables
=========

**Commonly Consumed Code Commodities** |Build Status| |Coverage Status|

Overview
--------

The reusables library is a reference of python functions and classes that
programmers may find themselves often recreating.

It is designed to not require any imports outside the standard library*,
but can be supplemented with those in the requirements.txt file for additional
functionality.

Tested on:

* Python 2.6+
* Python 3.3+
* Pypy


\* python 2.6 requires argparse


Example
~~~~~~~

.. code:: python

        import reusables

        reusables.extract_all("test/test_structure.zip", "my_archive")
        # All files in that zip will be extracted into directory "my_archive"

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

        reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
        # '/home/user/eViL User__/newdir____/new__file.txt'

        reusables.find_all_files(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']


Namespace
~~~~~~~~~

Also included is a Namespace class, similar to Bunch but designed so
that dictionaries are recursively made into namespaces.

.. code:: python

        from reusables import Namespace

        my_breakfast = {"spam": {"eggs": {"sausage": {"bacon": "yummy"}}}}
        namespace_breakfast = Namespace(**my_breakfast)

        print(namespace_breakfast.spam.eggs.sausage.bacon)
        # yummy

        print(namespace_breakfast.spam.eggs['sausage'].bacon)
        # yummy

        str(namespace_breakfast['spam'].eggs)
        # "{'sausage': {'bacon': 'yummy'}}"

        repr(namespace_breakfast)
        # "<Namespace: {'spam': {'eggs': {'sausage': {'...>"

        namespace_breakfast.to_dict()
        #{'spam': {'eggs': {'sausage': {'bacon': 'yummy'}}}}

        dict(namespace_breakfast)
        # {'spam': <Namespace: {'eggs': {'sausage': {'bacon': '...>}
        # This is NOT the same as .to_dict() as it is not recursive



Additional Info
---------------

This does not claim to provide the most accurate, fastest or most 'pythonic'
way to implement these useful snippets, this is simply designed for easy
reference. Any contributions that would help add functionality or
improve existing code is warmly welcomed!

Copyright (c) 2014-2016 - Chris Griffith - MIT License

.. |Build Status| image:: https://travis-ci.org/cdgriffith/Reusables.png?branch=master
   :target: https://travis-ci.org/cdgriffith/Reusables
.. |Coverage Status| image:: https://coveralls.io/repos/cdgriffith/Reusables/badge.png?branch=master
   :target: https://coveralls.io/r/cdgriffith/Reusables?branch=master
