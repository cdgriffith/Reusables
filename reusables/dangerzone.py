#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Dangerzone

Code in the dangerzone is either inherently dangerous by design  or not fully
tested and should never be used in production code. This may sound like a
generic warning like you would find with release candidate code, so let me
reiterate this point:

    This code will muck up your project if you use it.

Have fun!


Copyright (c) 2014  - Chris Griffith - MIT License
"""
import os
import sys
from reusables import Namespace, config_dict, python2x
_reuse_cache = dict()  # Could use DefaultDict but eh, it's another import


def reuse(func):
    """
    Save the variables entered into the function for reuse next time. Different
    from partials for the fact that it saves it to the original function,
    so that any module calling the default function will act as if it's a
    partial, and then may unknowingly change what the partial becomes!
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _reuse_cache
        cache = _reuse_cache.get(func.__name__, dict(args=[], kwargs={}))
        args = list(args)
        local_kwargs = cache['kwargs'].copy()
        if kwargs.get("reuse_view_cache"):
            del kwargs["reuse_view_cache"]
            return cache.copy()
        if kwargs.get("reuse_reset"):
            cache.update(dict(args=[], kwargs={}))
            del kwargs["reuse_reset"]
            return
        if kwargs.get("reuse_rep_args"):
            for old, new in kwargs["reuse_rep_args"]:
                if old in cache['args']:
                    tmp_args = list(cache['args'])
                    tmp_args[tmp_args.index(old)] = new
                    cache['args'] = tuple(tmp_args)
            del kwargs["reuse_rep_args"]
        args.extend(cache['args'][len(args):])
        local_kwargs.update(kwargs)
        result = func(*tuple(args), **local_kwargs)
        _reuse_cache[func.__name__] = dict(args=tuple(args),
                                           kwargs=local_kwargs)
        return result
    return wrapper

#TODO change to memory import
# That would allow for systems without disk access to work
def url_import(url, import_name):
    import tempfile
    import importlib
    try:
        import urllib.request as urllib
    except ImportError:
        import urllib

    tmpdir = tempfile.gettempdir()
    url = url.lower().strip()
    data = urllib.urlopen(url)
    filename = 'tempdir/{0}.py'.format(import_name)
    with open(filename, 'w') as outfile:
        outfile.write(data.read())
    sys.path.append(tmpdir)
    importlib.__import__(import_name)
    try:
        os.unlink(filename)
        os.rmdir(tmpdir)
    except OSError:
        print("Could not remove imported file")



#TODO consider options for a true Config namespace
class ConfigNamespace(Namespace):

    def __init__(self, config_file=None, auto_find=False,
                     verify=True, **cfg_options):
        cd = config_dict(config_file=config_file,
                         auto_find=auto_find,
                         verify=verify,
                         **cfg_options)
        self.config_file = config_file
        super(ConfigNamespace, self).__init__(**cd)

    def save(self, filename=None):
        if filename:
            self.config_file = filename