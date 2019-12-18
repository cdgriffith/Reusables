Changelog
=========

Version 0.9.5
-------------

- Adding `ignored` context manager (Thanks to Dogeek)

Version 0.9.4
-------------

- Adding sync_dirs function
- Adding sanitized_input function (Thanks to Dogeek)
- Breaking change: Changing find_files to return pathlib objects by default on Python 3.4+
- Removing python 2.6 from travis tests

Version 0.9.3
-------------

- Fixing imports in python 3.7

Version 0.9.2
-------------

- Adding option of kwargs to task for tasker
- Fixing documentations links

Version 0.9.1
-------------

- Fixing local imports not working when installed

Version 0.9.0
-------------

- Adding datetime_format, dtf methods
- Adding datetime_from_iso, dtiso methods
- Adding catch_it and retry_it wrappers
- Adding CONTRIBUTING file
- Changing Namespace now operates more like "dict" on init, and can accept both iterable and kwargs
- Changing major structure of reusables to better group similar functionality
- Changing wrapper time_it now uses .time for older versions instead of the .clock
- Depreciation Warning: get_logger is changing to setup_logger
- Breaking change: log_exception has new and changed kwargs
- Breaking change: removing Cookie Management in favor of separate library
- Breaking change: removing sort_by
- Breaking change: removing namespace.from_dict()
- Breaking change: removing DateTime class in favor of singular methods datetime_format and datetime_from_iso

Version 0.8.0
-------------

- Adding log_exception wrapper
- Adding ProtectedDict
- Adding hooks for Tasker main loop
- Adding roman number functions
- Adding directory_duplicates function
- Adding integer to words functions
- Adding option to enable scandir package walk instead of os.walk
- Adding url_to_ip and ip_to_url functions
- Adding hex_digest kwarg to file_hash
- Adding args and kwargs to time_it and log_exception wrappers
- Fixing file_hash checks by just passing to hashlib
- Changing functions to remove 'all' from them, extract_all, archive_all, find_all_files and find_all_files_generator
- Changing time_it function to use time.perf_counter on 3.3+ and time.clock on 2.6-3.2
- Depreciation Warning: extract_all is changing to extract
- Depreciation Warning: archive_all is changing to archive
- Depreciation Warning: find_all_files is changing to find_files
- Depreciation Warning: find_all_files_generator is changing to find_files_generator
- Depreciation Warning: count_all_files is changing to count_files
- Breaking change: Removing reuse wrapper
- Breaking change: archive_all now detects type based off name, should supply extension to name
- Breaking change: time_it message now takes args seconds, args, kwargs and does not allow positionals
- Breaking change: os_tree will no longer return an empty dictionary on failure, but include the base directory supplied
- Breaking change: renaming splice to cut

Version 0.7.0
-------------

- Adding archive_all and now methods
- Adding logger helpers to add stream and file handlers
- Adding depth and abspath to find files methods
- Adding head, tail, cat bash equivalents
- Adding command queue to Tasking class, to give commands asynchronously and without directly referencing the instance
- Changing test suite to have a common file it pulls imports and info from
- Changing logger helpers to accept string instead of logger
- Breaking change: Moving log formats from variables to Namespace log_formats
- Breaking change: Moving command line helpers to cli
- Breaking change: Command line helpers are not imported by default, should now use: from reusables.cli import *
- Breaking change: join_root has been better named join_here

Version 0.6.1
-------------

- Changing config_dict auto_find to accept a path to search at
- PyPI is stupid is why 0.6.0 is not up there

Version 0.6.0
-------------

- Adding multiprocessing helpers, Tasker class and run_in_pool
- Adding download and cmd helper functions
- Adding ThreadedServer class, for running a server (defaults to local file server) in the background
- Adding terminal analogue functions: cd, pwd, ls, pushd, popd
- Adding match_case option for find_all_files and count_all_files
- Fix 'run' call to CalledProcessError on older python versions
- Changing logger to _logger to be hidden by default (should not be breaking, if so you coded wrong)

Version 0.5.2
-------------

- Fix setup.py to use __init__.py instead of reusables.py for attrs

Version 0.5.1
-------------

- Adding default argument to confignamespace's int, float, list and boolean methods
- Adding change_logger_levels
- Changing __version__ location to __init__ so it can be accessed properly
- Changing protected_keys in Namespace to be hidden from documentation
- Changing linux only tests to be in their own class
- Breaking change: keyword arg position for confignamespace.list now has 'default' as first kwarg

Version 0.5.0
-------------

- Adding ConfigNamespace
- Adding lock wrapper for functions
- Adding duplicate file finder
- Adding easy CSV / list transformation
- Adding protected keys for namespaces
- Adding touch
- Adding extensions for scripts, binary and markup files
- Changing logging to be more explicit and run on sys.stdout
- Breaking change: removed command line running options and main function

Version 0.4.1
-------------

- Fixing Firefox dump command not working
- Adding MissingCookiesDB exception for clearer
- Wrapping commits with exceptions clauses for BrowserException
- Adding "created" and "expires" in _row_to_dict for Browsers

Version 0.4.0
-------------

- Breaking change: Removed 'dnd' from functions for clearer 'dry_run' or 'delete_on_success'
- Breaking change: Removing 'dangerzone' file, moving 'reuse' function to root namespace
- Added management tools for Firefox and Chrome cookies
- Added unique wrapper tool, ensures return value has not been returned before
- Changed all top level imports to have underscore before them like standard library

Version 0.3.0
-------------

- Namespace re-written to be more compatible with built-in dict
- Added support for rarfile extraction
- Adding PY2, PY3 as compliments of the booleans python3x to be similar to the six package
- Adding logging features
- Separating functionality to individual files
- Adding sphinx generated API documentation

Version 0.2.0
-------------

- Added DateTime class
- Added and rearranged several regular expression
- Added tree_view of dictionaries
- Added os_tree of a directory to a dictionary

Version 0.1.3
-------------

- Addition of Makefile
- Fixing issues with setup.py not including all needed files
- Tests now pass on windows by skipping some linux specific tests
- Improved config tests to only test against known sections, instead of entire dictionaries

Version 0.1.2
-------------

- Name change from reuse to reusables due to name already being registration on pypi

Version 0.1.1
-------------

- find_all_files_iter renamed to find_all_files_generator
- Added python2.6 and pypy testing and support
- Namespace is now a subclass of dict.
- Changing Readme into rst format.

Version 0.1
-----------

- initial release
