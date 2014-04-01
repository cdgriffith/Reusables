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
~~~~~~~~

.. code:: python

        import reusables

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

        reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
        # '/home/user/eViL User__/newdir____/new__file.txt'

        reusables.find_all_files(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']

		###
		### DateTime Class - Adds easy formatting to datetime objects
		###

	    reusables.DateTime().format("It's already {month-fullname} but it doesn't feel like {year-fullname} to me yet")
	    # "It's already April but it doesn't feel like 2014 to me yet"

		current_time = reusables.DateTime.now() # same as datetime.datetime.now(), returned as DateTime object

		current_time.format("Wake up {son}, it's {hours}:{minutes} {period}! I don't care if it's a {day-fullname}, {command}!",
							son="John",
							command="Get out of bed!")
		# "Wake up John, it's 09:51 AM! I don't care if it's a Saturday, Get out of bed!!"

		###
		### Namespace Class - Making dicts into easy to reference objects
		###


Overview
--------

Reusables doesn't have an overall theme or niche of functionality. Python
is often held high by developers that it is a 'batteries' included, and this
is simply another assorted battery pack.

The main functions are all in a single file that can also be copied into
any project, or simply copy the code you need directly into your project.

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

