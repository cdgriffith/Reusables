Reusables
=========

**Commonly Consumed Code Commodities** |Build Status| |Coverage Status|

Overview
--------

The reusables library is a reference of python functions and globals that
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

Design
------

Most python libraries are designed with the mindset of 'do exactly what
the input dictates, nothing else.' Which in general is the better way to
approach the problem allowing for the developer to fix their code.
However reusables is made to work with more human input. The idea is that it
will be used in cases like reading user inputted options or working with
python directly from the terminal or ipython.

Reusables with try smooth input into what you *really* wanted it to say.
Let's use joining paths as an example, it's uncommon to join two root
paths together and actually want just the second root path. Nor is it
common to have spaces before and after the path or filename and actually
want them there.

Reusables fixes your blunders for you:

.. code:: python

        join_paths('/home', '/user/', ' Desktop/example.file ')
        # '/home/user/Desktop/example.file'

However in these cases there is also a 'strict' option provided, which
should be used if you actually want exactly what you inputted, and are
just using the library for reference convenience.

.. code:: python

        join_paths('/home', '/user/', ' Desktop/example.file ', strict=True)
        # '/user/ Desktop/example.file '

What's in the box?
------------------

Here are some of the more useful features included:

Globals
~~~~~~~

+--------------+---------------------------------------------------------------------------+
| Global       | Definition                                                                |
+==============+===========================================================================+
| exts         | tuples of common file extensions (documents, music, video and pictures)   |
+--------------+---------------------------------------------------------------------------+
| regex        | regular expressions of interest                                           |
+--------------+---------------------------------------------------------------------------+
| python3x     | and python2x, boolean variables                                           |
+--------------+---------------------------------------------------------------------------+
| win\_based   | and nix\_based, to see what type of platform you are on                   |
+--------------+---------------------------------------------------------------------------+

Functions
~~~~~~~~~

+---------------------+------------------------------------------------------------------------------------------------------+
| Function            | Definition                                                                                           |
+=====================+======================================================================================================+
| join\_paths         | like os.path.join but will remove whitespace and extra separators                                    |
+---------------------+------------------------------------------------------------------------------------------------------+
| join\_root          | base path is automatically current working directory                                                 |
+---------------------+------------------------------------------------------------------------------------------------------+
| config\_dict        | reads config file(s) and returns results as a dictionary                                             |
+---------------------+------------------------------------------------------------------------------------------------------+
| config\_namespace   | automatically turns results of config\_dict into a Namespace                                         |
+---------------------+------------------------------------------------------------------------------------------------------+
| check\_filename     | see's if a filename is safe and human readable                                                       |
+---------------------+------------------------------------------------------------------------------------------------------+
| safe\_filename      | converts a string into a safe, human readable string that can be used as a filename                  |
+---------------------+------------------------------------------------------------------------------------------------------+
| safe\_path          | converts a potentially dangerous path into a safe one                                                |
+---------------------+------------------------------------------------------------------------------------------------------+
| file\_hash          | returns a hexdigest of a file's hash, read in blocks to avoid memory issues                          |
+---------------------+------------------------------------------------------------------------------------------------------+
| find\_all\_files    | hybrid of os.walk and glob.glob, search for files in directory, can specific name and/or extension   |
+---------------------+------------------------------------------------------------------------------------------------------+

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
        # {'sausage': {'bacon': 'yummy'}}

Additional Info
---------------

This does not claim to provide the most accurate, fastest or 'pythonic'
way to implement these useful snippets, this is simply designed for easy
reference. Any contributions that would help add functionality or
improve existing code is warmly welcomed!

Copyright (c) 2014 - Chris Griffith - MIT License

.. |Build Status| image:: https://travis-ci.org/cdgriffith/Reusables.png?branch=master
   :target: https://travis-ci.org/cdgriffith/Reusables
.. |Coverage Status| image:: https://coveralls.io/repos/cdgriffith/Reusables/badge.png?branch=master
   :target: https://coveralls.io/r/cdgriffith/Reusables?branch=master
