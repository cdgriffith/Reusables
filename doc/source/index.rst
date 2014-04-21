Reusables
=========

Commonly Consumed Code Commodities

.. toctree::
   :maxdepth: 2

The reusables library is a reference of python functions and classes that
programmers may find themselves often recreating.

It includes:

- Archive extraction
- Path (file and folders) management
- Friendly datetime formatting
- Easy config parsing
- Common regular expressions and file extensions
- Namespace class

As well as other fun and useful features.


Examples
--------

.. code:: python

        import reusables

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

        reusables.find_all_files(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']


DateTime Class
~~~~~~~~~~~~~~

Adds easy formatting to datetime objects. It also adds auto parsing for ISO formatted time.

.. code:: python

        current_time = reusables.DateTime() # same as datetime.datetime.now(), returned as DateTime object

        current_time.format("Wake up {son}, it's {hours}:{minutes} {period}! I don't care if it's a {day-fullname}, {command}!",
                            son="John",
                            command="Get out of bed!")
        # "Wake up John, it's 09:51 AM! I don't care if it's a Saturday, Get out of bed!!"


Namespace Class
~~~~~~~~~~~~~~~

Making dicts into easy to reference objects. Similar to Bunch but designed so
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

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

License
-------

The MIT License (MIT)

Copyright (c) 2014 Chris Griffith

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


