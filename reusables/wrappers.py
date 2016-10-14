#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2016  - Chris Griffith - MIT License
import time as _time
from threading import Lock as _Lock
from functools import wraps as _wraps

_g_lock = _Lock()
_unique_cache = dict()
_reuse_cache = dict()  # Could use DefaultDict but eh, it's another import


def unique(max_retries=10, wait=0, alt_return="-no_alt_return-",
           exception=Exception, error_text="No result was unique"):
    """Makes sure the function's return value has not been returned before
    or else it run with the same inputs again.

    :param max_retries: int of number of retries to attempt before failing
    :param wait: float of seconds to wait between each try, defaults to 0
    :param exception: Exception type of raise
    :param error_text: text of the exception
    :param alt_return: if specified, an exception is not raised on failure,
     instead the provided value of any type of will be returned
    """
    def func_wrap(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                value = func(*args, **kwargs)
                if value not in _unique_cache.setdefault(func.__name__, []):
                    _unique_cache[func.__name__].append(value)
                    return value
                if wait:
                    _time.sleep(wait)
            else:
                if alt_return != "-no_alt_return-":
                    return alt_return
                raise exception(error_text)
        return wrapper
    return func_wrap


def reuse(func):
    """
    Warning: Don't use this, just don't. If you need this you're probably coding
    wrong. This is for fun only.

    Save the variables entered into the function for reuse next time. Different
    from partials for the fact that it saves it to the original function,
    so that any module calling the default function will act as if it's a
    partial, and then may unknowingly change what the partial becomes!
    """

    @_wraps(func)
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


def lock_it(lock=_g_lock):
    """
    Simple wrapper to make sure a function is only run once at a time.

    :param lock: Which lock to use, uses unique default
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return func_wrapper
