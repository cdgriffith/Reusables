Changelog
=========
Version 0.5.0
-------------

- Adding lock wrapper for functions
- Adding duplicate file finder
- Adding easy CSV / list transformatio

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