Reusables
=========

**Commonly Consumed Code Commodities** |BuildStatus| |CoverageStatus| |DocStatus| |PyPi| |License|

Overview
--------

The reusables library is a reference of python functions and classes that
programmers may find themselves often recreating.

It includes:

- Cookie Management for Firefox and Chrome
- Archive extraction (zip, tar, rar)
- Path (file and folders) management
- Fast logging setup
- Namespace (dict to class modules with child recursion)
- Friendly datetime formatting
- Config to dict parsing
- Common regular expressions and file extensions
- Unique function wrappers

Reusables is designed to not require any imports outside the standard library,
but can be supplemented with those found in the requirements.txt file for
additional functionality.

CI tests run on:

* Python 2.6+
* Python 3.3+
* Pypy

Examples are provided below, and the API documentation can always be found at
readthedocs.org_.


What's in the box
-----------------

General Helpers and File Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

        import reusables

        reusables.extract_all("test/test_structure.zip", "my_archive")
        # All files in the zip will be extracted into directory "my_archive"

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

        reusables.find_all_files(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']

        reusables.count_all_files(".")
        # 405

        reusables.file_hash("test_structure.zip", hash_type="sha256")
        # 'bc11af55928ab89771b9a141fa526a5b8a3dbc7d6870fece9b91af5d345a75ea'

        reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
        # '/home/user/eViL User__/newdir____/new__file.txt'


Cookie Management
~~~~~~~~~~~~~~~~~

Firefox and Chrome Cookie management. (Chrome requires SQLite 3.8 or greater.)

.. code:: python

        fox = reusables.FirefoxCookies()
        # Automatically uses the DB of the default profile, can specify db=<path>

        fox.add_cookie("example.com", "MyCookie", "Cookie contents!")

        fox.find_cookies(host="Example")
        # [{'host': u'example.com', 'name': u'MyCookie', 'value': u'Cookie contents!'}]

        fox.delete_cookie("example.com", "MyCookie")

Namespace
~~~~~~~~~

Dictionary management class, similar to Bunch, but designed so
that sub-dictionaries are recursively made into namespaces.

.. code:: python

        my_breakfast = {"spam": {"eggs": {"sausage": {"bacon": "yummy"}}}}
        namespace_breakfast = reusables.Namespace(**my_breakfast)

        print(namespace_breakfast.spam.eggs.sausage.bacon)
        # yummy

        print(namespace_breakfast.spam.eggs['sausage'].bacon)
        # yummy

        str(namespace_breakfast['spam'].eggs)
        # "{'sausage': {'bacon': 'yummy'}}"

        namespace_breakfast.to_dict()
        #{'spam': {'eggs': {'sausage': {'bacon': 'yummy'}}}}

        dict(namespace_breakfast)
        # {'spam': <Namespace: {'eggs': {'sausage': {'bacon': '...>}
        # This is NOT the same as .to_dict() as it is not recursive



DateTime
~~~~~~~~

Easy formatting for datetime objects. It also adds auto parsing for ISO formatted time.


.. code:: python

        current_time = reusables.DateTime() # same as datetime.datetime.now(), as DateTime object

        current_time.format("Wake up {son}, it's {hours}:{minutes} {periods}!"
                            "I don't care if it's a {day-fullname}, {command}!",
                            son="John",
                            command="Get out of bed!")
        # "Wake up John, it's 09:51 AM! I don't care if it's a Saturday, Get out of bed!!"



Examples based on  Mon Mar 28 13:27:11 2016

===================== =================== ===========================
 Format                Mapping             Example
===================== =================== ===========================
{12-hour}               %I                 01
{24-hour}               %H                 13
{seconds}               %S                 14
{minutes}               %M                 20
{microseconds}          %f                 320944
{time-zone}             %Z
{years}                 %y                 16
{years-full}            %Y                 2016
{months}                %m                 03
{months-name}           %b                 Mar
{months-full}           %B                 March
{days}                  %d                 28
{week-days}             %w                 1
{year-days}             %j                 088
{days-name}             %a                 Mon
{days-full}             %A                 Monday
{mon-weeks}             %W                 13
{date}                  %x                 03/28/16
{time}                  %X                 13:27:11
{date-time}             %C                 Mon Mar 28 13:27:11 2016
{utc-offset}            %Z
{periods}               %p                 PM
{iso-format}            %Y-%m-%dT%H:%M:%S  2016-03-28T13:27:11
===================== =================== ===========================


Logging
~~~~~~~

.. code:: python

        logger = reusables.get_logger(__name__)
        # By default it adds a stream logger to sys.stderr

        logger.info("Test")
        # 2016-04-25 19:32:45,542 __main__     INFO     Test


There are multiple log formatters provided, as well as additional helper functions


.. code:: python

        reusables.remove_stream_handlers(logger)
        # remove_file_handlers() and remove_all_handlers() also available

        stream_handler = reusables.get_stream_handler(log_format=reusables.log_detailed_format)
        logger.addHandler(stream_handler)
        logger.info("Example log entry")
        # 2016-04-25 19:42:52,633 : 315147 MainThread : reusables.log INFO Example log entry


Because ReStructuredText tables don't preserve whitespace (even with literals), which is important to show distinction in these formatters, here's it in a code block instead.

.. code::

    +------------------------+--------------------------------------------------------------------------------------+
    | Formatter              | Example Output                                                                       |
    +========================+======================================================================================+
    | log_easy_read_format   | 2016-04-26 21:17:51,225 - example_logger  INFO      example log message              |
    |                        | 2016-04-26 21:17:59,074 - example_logger  ERROR     Something broke                  |
    +------------------------+--------------------------------------------------------------------------------------+
    | log_detailed_format    | 2016-04-26 21:17:51,225 :  7020 MainThread : example_logger INFO example log message |
    |                        | 2016-04-26 21:17:59,074 : 14868 MainThread : example_logger ERROR Something broke    |
    +------------------------+--------------------------------------------------------------------------------------+
    | log_level_first_format | INFO - example_logger - 2016-04-26 21:17:51,225 - example log message                |
    |                        | ERROR - example_logger - 2016-04-26 21:17:59,074 - Something broke                   |
    +------------------------+--------------------------------------------------------------------------------------+
    | log_threaded_format    | 7020 MainThread : example log message                                                |
    |                        | 14868 MainThread : Something broke                                                   |
    +------------------------+--------------------------------------------------------------------------------------+
    | log_easy_thread_format |  7020 MainThread : example_logger  INFO      example log message                     |
    |                        | 14868 MainThread : example_logger  ERROR     Something broke                         |
    +------------------------+--------------------------------------------------------------------------------------+
    | log_common_format      | 2016-04-26 21:17:51,225 - example_logger - INFO - example log message                |
    |                        | 2016-04-26 21:17:59,074 - example_logger - ERROR - Something broke                   |
    +------------------------+--------------------------------------------------------------------------------------+


Extension Groups
~~~~~~~~~~~~~~~~

It's common to be looking for a specific type of file.

.. code:: python

        if file_path.endswith(reusables.exts.pictures):
            print("{} is a picture file".format(file_path))

That's right, str.endswith_ (as well as str.startswith_) accept a tuple to search.

===================== ===================
 File Type             Extensions
===================== ===================
 pictures              .jpeg .jpg .png .gif .bmp .tif .tiff .ico .mng .tga .psd .xcf .svg .icns
 video                 .mkv .avi .mp4 .mov .flv .mpeg .mpg .3gp .m4v .ogv .asf .m1v .m2v .mpe .ogv .wmv .rm .qt
 music                 .mp3 .ogg .wav .flac .aif .aiff .au .m4a .wma .mp2 .m4a .m4p .aac .ra .mid .midi .mus .psf
 documents             .doc .docx .pdf .xls .xlsx .ppt .pptx .csv .epub .gdoc .odt .rtf .txt .info .xps .gslides .gsheet
 archives              .zip .rar .7z .tar.gz .tgz .gz .bzip .bzip2 .bz2 .xz .lzma .bin .tar
 cd_images             .iso .nrg .img .mds .mdf .cue .daa
===================== ===================


Wrappers
~~~~~~~~

There are tons of wrappers for caching and saving inputs and outputs, this is a
different take that requires the function returns a result not yet provided.

.. code:: python

    @reusables.unique(max_retries=100, error_text="All UIDs taken!")
    def gen_small_uid():
        import random
        return random.randint(0, 100)



Common Issues
-------------

**UnRAR path issues**


A common error to see, especially on Windows based systems, is: "rarfile.RarCannotExec: Unrar not installed? (rarfile.UNRAR_TOOL='unrar')"

This is probably because unrar is not downloaded or linked properly. Download UnRAR
from http://www.rarlab.com/rar_add.htm and follow these instructions before
trying again: http://rarfile.readthedocs.org/en/latest/faq.html?highlight=windows#how-can-i-get-it-work-on-windows

License
-------

The MIT License (MIT)

Copyright (c) 2014-2016 Chris Griffith

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


.. |BuildStatus| image:: https://travis-ci.org/cdgriffith/Reusables.png?branch=master
   :target: https://travis-ci.org/cdgriffith/Reusables
.. |CoverageStatus| image:: https://img.shields.io/coveralls/cdgriffith/Reusables/master.svg?maxAge=2592000
   :target: https://coveralls.io/r/cdgriffith/Reusables?branch=master
.. |DocStatus| image:: https://readthedocs.org/projects/reusables/badge/?version=latest
   :target: http://reusables.readthedocs.org/en/latest/index.html
.. |PyPi| image:: https://img.shields.io/pypi/v/reusables.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/reusables/
.. |License| image:: https://img.shields.io/pypi/l/reusables.svg
   :target: https://pypi.python.org/pypi/reusables/
.. _str.endswith: https://docs.python.org/2/library/stdtypes.html#str.endswith
.. _str.startswith: https://docs.python.org/2/library/stdtypes.html#str.startswith
.. _readthedocs.org: http://reusables.readthedocs.io/en/latest/

Additional Info
---------------

This does not claim to provide the most accurate, fastest or most 'pythonic'
way to implement these useful snippets, this is simply designed for easy
reference. Any contributions that would help add functionality or
improve existing code is warmly welcomed!

.. toctree::
   :maxdepth: 2

   reusables
   browser
   log
   datetime
   namespace
   wrappers
   changelog
