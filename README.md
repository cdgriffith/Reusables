# Reusables
**Commonly Consumed Code Commodities**
[![Build Status](https://travis-ci.org/cdgriffith/Reusables.png?branch=master)](https://travis-ci.org/cdgriffith/Reusables)
[![Coverage Status](https://coveralls.io/repos/cdgriffith/Reusables/badge.png?branch=master)](https://coveralls.io/r/cdgriffith/Reusables?branch=master)

## Overview

<!--- start description --->

The reuse library is a reference of python functions and globals
that programmers may find themselves often recreating.

<!--- end description --->

Example functions:

```python
    import reuse

    reuse.config_dict('my_config.cfg')
    # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

    reuse.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
    # '/home/user/eViL User__/newdir____/new__file.txt'

    reuse.find_all_files(".", ext=reuse.exts.pictures)
    # ['/home/user/background.jpg', '/home/user/private.png']
```

## Design

Most python libraries are designed with the mindset of 'do exactly what the
input dictates, nothing else.' Which in general is the better way to approach
the problem allowing for the developer to fix their code. However reusables
is made to work with more human input. The idea is that it will be used
in cases like reading user inputted options or working with python
directly from the terminal or ipython.

Reusables with try smooth input into what you *really* wanted it to say.
Let's use joining paths as an example, it's uncommon to join two root paths together
and actually want just the second root path. Nor is it common to have spaces
before and after the path or filename and actually want them there.

Reusables fixes your blunders for you:
```python
    join_paths('/home', '/user/', ' Desktop/example.file ')
    # '/home/user/Desktop/example.file'
```

However in these cases there is also a 'strict' option provided, which should be
used if you actually want exactly what you inputted, and are just using the
library for reference convenience.

```python
    join_paths('/home', '/user/', ' Desktop/example.file ', strict=True)
    # '/user/ Desktop/example.file '
```

## What's in the box?

Here are some of the more useful features included:

### Globals

 global  |  definition
-------- | ------------
exts     | tuples of common file extensions (documents, music, video and pictures)
regex    | regular expressions of interest
python3x | and python2x, boolean variables
win_based | and nix_based, to see what type of platform you are on

### Functions

 functions  |  definition
----------- | ------------
join_paths | like os.path.join but will remove whitespace and extra separators
join_root | base path is automatically current working directory
config_dict | reads config file(s) and returns results as a dictionary
config_namespace | automatically turns results of config_dict into a Namespace
check_filename | see's if a filename is safe and human readable
safe_filename | converts a string into a safe, human readable string that can be used as a filename
safe_path | converts a potentially dangerous path into a safe one
file_hash | returns a hexdigest of a file's hash, read in blocks to avoid memory issues
find_all_files | hybrid of os.walk and glob.glob, search for files in directory, can specific name and/or extension

### Extras

Also included is a Namespace class, similar to Bunch but designed so that dictionaries
are recursively made into namespaces, and can be treated as either a
dict or a namespace when accessed.

```python

    from reuse import Namespace

    my_breakfast = {"spam" : {"eggs": {"sausage": {"bacon": "yummy"}}}}
    namespace_breakfast = Namespace(\*\*my\_breakfast)

    print(namespace_breakfast.spam.eggs.sausage.bacon)
    # yummy

    print(namespace_breakfast.spam.eggs\[\'sausage\'\].bacon)
    # yummy

    str(namespace_breakfast['spam'].eggs)
    # "{'sausage': {'bacon': 'yummy'}}"

    # Don't use dict() on Namespace objects, use .to_dict()
    namespace_breakfast.spam.eggs['sausage'].to_dict()
    # {'sausage': {'bacon': 'yummy'}}

```

## Additional Info

This does not claim to provide the most accurate, fastest or 'pythonic' way to
implement these useful snippets, this is simply designed for easy reference.
Any contributions that would help add functionality or improve existing
code is warmly welcomed\!

Copyright \(c\) 2014  \- Chris Griffith \- MIT License