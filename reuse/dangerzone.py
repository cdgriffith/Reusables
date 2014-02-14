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
