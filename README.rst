Reusables
=========

**Commonly Consumed Code Commodities** |Build Status| |Coverage Status|

Overview
--------

The reusables library is a reference of python functions and classes that
programmers may find themselves often recreating.

Example
~~~~~~~

.. code:: python

        import reusables

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

        reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
        # '/home/user/eViL User__/newdir____/new__file.txt'

        reusables.find_all_files(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']


Extras
~~~~~~

Also included is a Namespace class, similar to Bunch but designed so
that dictionaries are recursively made into namespaces, and can be
treated as either a dict or a namespace when accessed.

.. code:: python

        from reusables import Namespace

        my_breakfast = {"spam" : {"eggs": {"sausage": {"bacon": "yummy"}}}}
        namespace_breakfast = Namespace(**my_breakfast)

        print(namespace_breakfast.spam.eggs.sausage.bacon)
        # yummy

        print(namespace_breakfast.spam.eggs['sausage'].bacon)
        # yummy

        str(namespace_breakfast['spam'].eggs)
        # "{'sausage': {'bacon': 'yummy'}}"

        dict(namespace_breakfast.spam.eggs['sausage'])
        # {'bacon': 'yummy'}

        repr(namespace_breakfast)
        # "<Namespace: {'spam': {'eggs': {'sausage': {'...>"

Additional Info
---------------

This does not claim to provide the most accurate, fastest or most 'pythonic'
way to implement these useful snippets, this is simply designed for easy
reference. Any contributions that would help add functionality or
improve existing code is warmly welcomed!

Copyright (c) 2014 - Chris Griffith - MIT License

.. |Build Status| image:: https://travis-ci.org/cdgriffith/Reusables.png?branch=master
   :target: https://travis-ci.org/cdgriffith/Reusables
.. |Coverage Status| image:: https://coveralls.io/repos/cdgriffith/Reusables/badge.png?branch=master
   :target: https://coveralls.io/r/cdgriffith/Reusables?branch=master
