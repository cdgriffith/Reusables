#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2016  - Chris Griffith - MIT License
import time as _time
from threading import Lock as _Lock
from functools import wraps as _wraps
import logging as _logging
try:
    import queue as _queue
except ImportError:
    import Queue as _queue

_logger = _logging.getLogger("reusables.wrappers")
_g_lock = _Lock()
_g_queue = _queue.Queue()
_unique_cache = dict()
_reuse_cache = dict()  # Could use DefaultDict but eh, it's another import


def unique(max_retries=10, wait=0, alt_return="-no_alt_return-",
           exception=Exception, error_text="No result was unique"):
    """
    Wrapper. Makes sure the function's return value has not been returned before
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
    Wrapper.

    .. warning::

        Don't use this, just don't. If you need this you're probably coding
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
    Wrapper. Simple wrapper to make sure a function is only run once at a time.

    :param lock: Which lock to use, uses unique default
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return func_wrapper


def time_it(log=False, message="Function took a total of {0} seconds",
            append=None):
    """
    Wrapper. Time the amount of time it takes the execution of the function
    and print it.

    If log is true, make sure to set the logging level of 'reusables' to INFO
    level or lower.

    .. code:: python

        import time
        import reusables

        reusables.add_stream_handler('reusables')

        @reusables.time_it(log=True, message="{0:.2f} seconds")
        def test_time(length):
            time.sleep(length)
            return "slept {0}".format(length)

        result = test_time(5)
        # 2016-11-09 16:59:39,935 - reusables.wrappers  INFO      5.01 seconds

        print(result)
        # slept 5

    :param log: log as INFO level instead of printing
    :param message: string to format with total time as the only input
    :param append: list to append item too
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            start_time = _time.time()
            try:
                return func(*args, **kwargs)
            finally:
                total_time = _time.time() - start_time
                if log:
                    logger = _logging.getLogger(log) if isinstance(log, str)\
                        else _logger
                    logger.info(message.format(total_time))
                else:
                    print(message.format(total_time))
                if isinstance(append, list):
                    append.append(total_time)
        return wrapper
    return func_wrapper


def queue_it(queue=_g_queue, **put_args):
    """
    Wrapper. Instead of returning the result of the function, add it to a queue.

    :param queue: Queue to add result into
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            queue.put(func(*args, **kwargs), **put_args)
        return wrapper
    return func_wrapper


def log_exception(log="reusables", message="Exception in {func_name} - {err}",
                  exception=None, exception_message="Error in {func_name}"):
    """
    Wrapper. Log the traceback to any exceptions raised. Possible to raise
    custom exception.

    .. code :: python

        @reusables.log_exception()
        def test():
            raise Exception("Bad")

        # 2016-12-26 12:38:01,381 - reusables   ERROR  Exception in test - Bad
        # Traceback (most recent call last):
        #     File "<input>", line 1, in <module>
        #     File "reusables\wrappers.py", line 200, in wrapper
        #     raise err
        # Exception: Bad

    :param log: log name to use
    :param message: message to use in log
    :param exception: custom exception to raise instead of what was raised
    :param exception_message: message for the custom exception
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                logger = (_logging.getLogger(log) if isinstance(log, str)
                          else _logger)
                logger.exception(message.format(func_name=func.__name__,
                                                err=str(err)))
                if exception:
                    raise exception(exception_message.format(
                        func_name=func.__name__, err=str(err)))
                raise err
        return wrapper
    return func_wrapper
