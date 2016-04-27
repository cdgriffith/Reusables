Reusables
=========

**Commonly Consumed Code Commodities** |Build Status| |Coverage Status|

Overview
--------

The reusables library is a reference of python functions and classes that
programmers may find themselves often recreating.

It includes:

- Archive extraction (zip, tar, rar)
- Path (file and folders) management
- Friendly datetime formatting
- Easy config parsing
- Common regular expressions and file extensions
- Namespace class
- Fast logging setup
- Additional fun and useful features

Reusables is designed to not require any imports outside the standard library*,
but can be supplemented with those in the requirements.txt file for additional
functionality.

Tested on:

* Python 2.6+
* Python 3.3+
* Pypy


\* python 2.6 requires argparse


Examples
--------

General Helpers
~~~~~~~~~~~~~~~

.. code:: python

        import reusables

        reusables.extract_all("test/test_structure.zip", "my_archive")
        # All files in the zip will be extracted into directory "my_archive"

        reusables.config_dict('my_config.cfg')
        # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}


File Management
~~~~~~~~~~~~~~~

.. code:: python

        reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
        # '/home/user/eViL User__/newdir____/new__file.txt'

        reusables.find_all_files(".", ext=reusables.exts.pictures)
        # ['/home/user/background.jpg', '/home/user/private.png']

        reusables.count_all_files(".")
        # 405

        reusables.file_hash("test_structure.zip", hash_type="sha256")
        # 'bc11af55928ab89771b9a141fa526a5b8a3dbc7d6870fece9b91af5d345a75ea'



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

        current_time = reusables.DateTime() # same as datetime.datetime.now(), returned as DateTime object

        current_time.format("Wake up {son}, it's {hours}:{minutes} {periods}!"
                            "I don't care if it's a {day-fullname}, {command}!",
                            son="John",
                            command="Get out of bed!")
        # "Wake up John, it's 09:51 AM! I don't care if it's a Saturday, Get out of bed!!"



Examples based on : Mon Mar 28 13:27:11 2016

===================== =================== ===========================
 Format                Mapping             Example
--------------------- ------------------- ---------------------------
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

Extension Groups
~~~~~~~~~~~~~~~~

It's common to be looking for a specific type of file.

.. code:: python

        if file.endswith(reusables.exts.pictures):
            print("{} is a picture file".format(file))

That's right, `str.endswith <https://docs.python.org/2/library/stdtypes.html#str.endswith>` (as well as str.startswith) accept a tuple to search.

===================== =================== 
 File Type             Extensions
--------------------- -------------------
 pictures              .jpeg .jpg .png .gif .bmp .tif .tiff
                       .ico .mng .tga .psd .xcf .svg .icns
 video                 .mkv .avi .mp4 .mov .flv .mpeg .mpg .3gp
                       .m4v .ogv .asf .m1v .m2v .mpe .ogv .wmv
                       .rm .qt
 music                 .mp3 .ogg .wav .flac .aif .aiff .au .m4a
                       .wma .mp2 .m4a .m4p .aac .ra .mid .midi
                       .mus .psf
 documents             .doc .docx .pdf .xls .xlsx .ppt .pptx
                       .csv .epub .gdoc .odt .rtf .txt .info
                       .xps .gslides .gsheet
 archives              .zip .rar .7z .tar.gz .tgz .gz .bzip
                       .bzip2 .bz2 .xz .lzma .bin .tar
 cd_images             .iso .nrg .img .mds .mdf .cue .daa
--------------------- ------------------


Common Issues
-------------

**UnRAR path issues**

A common error to see, espeically on Windows based systems, is: "rarfile.RarCannotExec: Unrar not installed? (rarfile.UNRAR_TOOL='unrar')"

This is probably because unrar is not downloaded or linked properly. Download UnRAR
from http://www.rarlab.com/rar_add.htm and follow these instructions before trying again: http://rarfile.readthedocs.org/en/latest/faq.html?highlight=windows#how-can-i-get-it-work-on-windows



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
