Reusables
=========

Commonly Consumed Code Commodities

.. toctree::
   :maxdepth: 2

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


Overview
--------

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

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

