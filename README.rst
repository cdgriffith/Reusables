Reusables
=========

|BuildStatus| |CoverageStatus| |License| |PyPi| |DocStatus|

**Commonly Consumed Code Commodities**

Overview
--------

The reusables library is a cookbook of python functions and classes that
programmers may find themselves often recreating.

It includes:

- Archiving and extraction for zip, tar, gz, bz2, and rar
- Path (file and folders) management
- Fast logging setup and tools
- Namespace (dict to class modules with child recursion)
- Friendly datetime formatting
- Config to dict parsing
- Common regular expressions and file extensions
- Helpful wrappers
- Bash analogues
- Easy downloading
- Multiprocessing helpers

Install
~~~~~~~

Reusables is on PyPI, so can be easily installed with pip or easy_install.

.. code::

   pip install reusables


There are no required decencies. If this doesn't work, it's broken, raise
a github issue.

Reusables is designed to not require any imports outside the standard library,
but can be supplemented with those found in the requirements.txt file for
additional functionality.

CI tests run on:

* Python 2.6+
* Python 3.3+
* Pypy

Examples are provided below, and the API documentation can always be found at
readthedocs.org_.

Please note this is currently in development. Any item in development
prior to a major version (1.x, 2.x) may change. Once at a major version,
no breaking changes are planned to occur within that version.

What's in the box
-----------------

General Helpers and File Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

        import reusables

        reusables.find_files_list(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']

        reusables.archive("reusables", name="reuse", archive_type="zip")
        # 'C:\\Users\\Me\\Reusables\\reuse.zip'

        reusables.extract("test/test_structure.zip", "my_archive")
        # All files in the zip will be extracted into directory "my_archive"

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

        reusables.count_files(".")
        # 405

        reusables.file_hash("test_structure.zip", hash_type="sha256")
        # 'bc11af55928ab89771b9a141fa526a5b8a3dbc7d6870fece9b91af5d345a75ea'

        reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
        # '/home/user/eViL User__/newdir____/new__file.txt'

        reusables.run("echo 'hello there!'", shell=True)
        # CompletedProcess(args="echo 'hello there!'", returncode=0, stdout='hello there!\n')

        reusables.cut("abcdefghi")
        # ['ab', 'cd', 'ef', 'gh', 'i']


One of the most reusables pieces of code is the find_files. It is always
appearing on stackoverflow and forums of how to implement os.walk or glob;
here's both.

.. code:: python

         reusables.find_files_list(".", name="*reuse*", depth=2)
         # ['.\\test\\test_reuse.py', '.\\test\\test_reuse_datetime.py',
         #  '.\\test\\test_reuse_logging.py', '.\\test\\test_reuse_namespace.py']

         # match_case works for both ext and name
         # depth of 1 means this working directory only, no further

         reusables.find_files_list(ext=".PY", depth=1, match_case=True)
         # []

         reusables.find_files_list(ext=".py", depth=1, match_case=True)
         # ['.\\setup.py']

         reusables.find_files_list(name="setup", ext=".py", match_case=True)
         # ['.\\setup.py']

         reusables.find_files_list(name="Setup", ext=".py", match_case=True)
         # []


Namespace
~~~~~~~~~

Check out Box_, a much improved version as its own library.

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

Logging
~~~~~~~

.. code:: python

        logger = reusables.setup_logger(__name__)
        # By default it adds a stream logger to sys.stderr

        logger.info("Test")
        # 2016-04-25 19:32:45,542 __main__     INFO     Test


There are multiple log formatters provided, as well as additional helper functions.
All helper functions will accept either the logger object or the name of the logger.

.. code:: python

        reusables.remove_stream_handlers(__name__)
        # remove_file_handlers() and remove_all_handlers() also available

        reusables.add_stream_handler(__name__, log_format=reusables.log_formats.detailed)
        r.add_rotating_file_handler(__name__, "my.log", level=logging.INFO)

        logger.info("Example log entry")
        # 2016-12-14 20:56:55,446 : 315147 MainThread : reusables.log INFO Example log entry

        open("my.log").read()
        # 2016-12-14 20:56:55,446 - __builtin__   INFO     Example log entry


**Provided log formats**

Feel free to provide your own formats, aided by the docs_. However this includes
some commonly used ones you may find useful. they are all stored in the Namespace
"reusables.log_formats" (feel free to use it as a dict as stated above).

Because ReStructuredText tables don't preserve whitespace (even with literals),
 which is important to show distinction in these formatters, here's it in a code block instead.

.. code:: python

    reusables.log_formats.keys()
    # ['common', 'level_first', 'threaded', 'easy_read', 'easy_thread', 'detailed']

    logger = reusables.setup_logger(__name__, log_format=reusables.log_formats.threaded)
    reusables.add_timed_rotating_file_handler(logger, "timed.log", level=logging.ERROR, log_format=reusables.log_formats.detailed)


.. code::

    +--------------+--------------------------------------------------------------------------------------+
    | Formatter    | Example Output                                                                       |
    +==============+======================================================================================+
    | easy_read    | 2016-04-26 21:17:51,225 - example_logger  INFO      example log message              |
    |              | 2016-04-26 21:17:59,074 - example_logger  ERROR     Something broke                  |
    +--------------+--------------------------------------------------------------------------------------+
    | detailed     | 2016-04-26 21:17:51,225 :  7020 MainThread : example_logger INFO example log message |
    |              | 2016-04-26 21:17:59,074 : 14868 MainThread : example_logger ERROR Something broke    |
    +--------------+--------------------------------------------------------------------------------------+
    | level_first  | INFO - example_logger - 2016-04-26 21:17:51,225 - example log message                |
    |              | ERROR - example_logger - 2016-04-26 21:17:59,074 - Something broke                   |
    +--------------+--------------------------------------------------------------------------------------+
    | threaded     | 7020 MainThread : example log message                                                |
    |              | 14868 MainThread : Something broke                                                   |
    +--------------+--------------------------------------------------------------------------------------+
    | easy_thread  |  7020 MainThread : example_logger  INFO      example log message                     |
    |              | 14868 MainThread : example_logger  ERROR     Something broke                         |
    +--------------+--------------------------------------------------------------------------------------+
    | common       | 2016-04-26 21:17:51,225 - example_logger - INFO - example log message                |
    |              | 2016-04-26 21:17:59,074 - example_logger - ERROR - Something broke                   |
    +--------------+--------------------------------------------------------------------------------------+


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
 video                 .mkv .avi .mp4 .mov .flv .mpeg .mpg .3gp .m4v .ogv .asf .m1v .m2v .mpe .ogv .wmv .rm .qt .3g2 .asf .vob
 music                 .mp3 .ogg .wav .flac .aif .aiff .au .m4a .wma .mp2 .m4a .m4p .aac .ra .mid .midi .mus .psf
 documents             .doc .docx .pdf .xls .xlsx .ppt .pptx .csv .epub .gdoc .odt .rtf .txt .info .xps .gslides .gsheet .pages .msg .tex .wpd .wps .csv
 archives              .zip .rar .7z .tar.gz .tgz .gz .bzip .bzip2 .bz2 .xz .lzma .bin .tar
 cd_images             .iso .nrg .img .mds .mdf .cue .daa
 scripts               .py .sh .bat
 binaries              .msi .exe
 markup                .html .htm .xml .yaml .json .raml .xhtml .kml
===================== ===================


Wrappers
~~~~~~~~

**unique**

There are tons of wrappers for caching and saving inputs and outputs, this is a
different take that requires the function returns a result not yet provided.

.. code:: python

    @reusables.unique(max_retries=100, error_text="All UIDs taken!")
    def gen_small_uid():
        return random.randint(0, 100)

**time_it**

Easily time the execution time of a function, using the high precision
perf_conuter on Python 3.3+, otherwise clock.

.. code:: python

    @reusables.time_it()
    def test_it():
        return time.sleep(float(f"0.{random.randint(1, 9)}"))



Command line helpers
--------------------

Use the Python interpreter as much as a shell? Here's some handy helpers to
fill the void. (Please don't do 'import \*' in production code, this is used
as an easy to use example using the interpreter interactively.)

> These are not imported by default with "import reusables", as they are designed to be imported only in an interactive shell

Some commands from other areas are also included where they are highly applicable in both
instances, such as 'touch' and 'download'.


.. code:: python

        from reusables.cli import *

        cd("~") # Automatic user expansion unlike os.chdir()

        pwd()
        # '/home/user'

        pushd("Downloads")
        # ['Downloads', '/home/user']

        pwd()
        # '/home/user/Downloads'

        popd()
        # ['/home/user']

        ls("-lah")  # Uses 'ls' on linux and 'dir' on windows
        #  total 1.5M
        #  drwxr-xr-x 49 james james 4.0K Nov  1 20:09 .
        #  drwxr-xr-x  3 root  root  4.0K Aug 21  2015 ..
        #  -rw-rw-r--  1 james james  22K Aug 22 13:21 picture.jpg
        #  -rw-------  1 james james  17K Nov  1 20:08 .bash_history

        cmd("ifconfig") # Shells, decodes and prints 'reusables.run' output
        #   eth0      Link encap:Ethernet  HWaddr de:ad:be:ef:00:00
        #             inet addr:10.0.2.5  Bcast:10.0.2.255  Mask:255.255.255.0
        #             ...

        download('https://www.python.org/ftp/python/README.html', save_to_file=False)
        # 2016-11-02 10:37:23,644 - reusables.web  INFO      Downloading https://www.python.org/ftp/python/README.html (2.3 KB) to memory
        # b'<PRE>\nPython Distribution...

DateTime
~~~~~~~~

Easy formatting for datetime objects. Also parsing for ISO formatted time.


.. code:: python

        reusables.datetime_format("Wake up {son}, it's {hours}:{minutes} {periods}!"
                            "I don't care if it's a {day-fullname}, {command}!",
                            son="John",
                            command="Get out of bed!")
        # "Wake up John, it's 09:51 AM! I don't care if it's a Saturday, Get out of bed!!"

        reusables.datetime_from_iso('2019-03-10T12:56:55.031863')
        # datetime.datetime(2019, 3, 10, 12, 56, 55, 31863)


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


FAQ
---

**How can I help? / Why doesn't it do what I want it too?**

Please feel free to make suggestions in the 'issues' section of github, or to be super duper helpful go ahead and submit a PR for the
functionality you want to see! Only requirements are that it's well thought out and is more in place here rather than it's own project
(to be merged will need documentation and basic unittests as well, but not a requirement for opening the PR).
Please don't hesitate if you're new to python! Even the smallest PR contributions will earn a mention in a brand new Contributors section.

**Unrar not installed?**

A common error to see, especially on Windows based systems, is: "rarfile.RarCannotExec: Unrar not installed? (rarfile.UNRAR_TOOL='unrar')"

This is probably because unrar is not downloaded or linked properly. Download UnRAR
from http://www.rarlab.com/rar_add.htm and follow these instructions before
trying again: http://rarfile.readthedocs.org/en/latest/faq.html?highlight=windows#how-can-i-get-it-work-on-windows

License
-------

The MIT License (MIT)

Copyright (c) 2014-2019 Chris Griffith

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
.. _docs: https://docs.python.org/3/library/logging.html#logrecord-attributes
.. _Box: https://pypi.python.org/pypi/python-box

Additional Info
---------------

This does not claim to provide the most accurate, fastest or most 'pythonic'
way to implement these useful snippets, this is simply designed for easy
reference. Any contributions that would help add functionality or
improve existing code is warmly welcomed!
