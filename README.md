# Reusables
**Convenient Consolidated Commonly Consumed Code Commodities**
[![Build Status](https://travis-ci.org/cdgriffith/Reusables.png?branch=master)](https://travis-ci.org/cdgriffith/Reusables)
[![Coverage Status](https://coveralls.io/repos/cdgriffith/Reusables/badge.png?branch=master)](https://coveralls.io/r/cdgriffith/Reusables?branch=master)

## Overview

The reusables library is a convenient reference of python functions and globals
that are widely implemented throughout different projects.

```python

    import reusables

    reusables.python_version
    # (2, 7, 5)

    reusables.python3x
    # False

    reusables.config_dict('my_config.cfg')
    # {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}

    reusables.safe_path('/home/user/eViL User\0\\/newdir$^&*/new^%file.txt')
    # '/home/user/eViL User__/newdir____/new__file.txt'

```

## Design

Most python libraries are designed with the mindset of 'do exactly what the
input dictates, nothing else.' Which in general is the better way to approach
the problem allowing for the developer to fix their code. However reusables
is made to work with more human input. The idea is that it will be used
in cases like reading user inputted options or working with python
directly from the terminal.

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

## Additional Info

This does not claim to provide the most accurate, fastest or 'pythonic' way to
implement these useful snippets, this is simply designed for easy reference.
Any contributions that would help add functionality or improve existing
code is warmly welcomed\!

Copyright \(c\) 2014  \- Chris Griffith \- MIT License