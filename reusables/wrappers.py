#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
import time as _time
from threading import Lock as _Lock
from functools import wraps as _wraps
import logging as _logging
try:
    import queue as _queue
except ImportError:
    import Queue as _queue

from .shared_variables import python_version

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

    .. code: python

        import reusables
        import random

        @reusables.unique(max_retries=100)
        def poor_uuid():
            return random.randint(0, 10)

        print([poor_uuid() for _ in range(10)])
        # [8, 9, 6, 3, 0, 7, 2, 5, 4, 10]

        print([poor_uuid() for _ in range(100)])
        # Exception: No result was unique

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


def lock_it(lock=_g_lock):
    """
    Wrapper. Simple wrapper to make sure a function is only run once at a time.

    .. code: python

        import reusables
        import time

        def func_one(_):
            time.sleep(5)

        @reusables.lock_it()
        def func_two(_):
            time.sleep(5)

        @reusables.time_it(message="test_1 took {0:.2f} seconds")
        def test_1():
            reusables.run_in_pool(func_one, (1, 2, 3), threaded=True)

        @reusables.time_it(message="test_2 took {0:.2f} seconds")
        def test_2():
            reusables.run_in_pool(func_two, (1, 2, 3), threaded=True)

        test_1()
        test_2()

        # test_1 took 5.04 seconds
        # test_2 took 15.07 seconds


    :param lock: Which lock to use, uses unique default
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return func_wrapper


def time_it(log=None, message="Function took a total of {seconds} seconds "
                              "with args: {args} - kwargs: {kwargs}",
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

        @reusables.time_it(log=True, message="{seconds:.2f} seconds")
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
            time_func = (_time.perf_counter if python_version >= (3, 3)
                         else _time.clock)
            start_time = time_func()
            try:
                return func(*args, **kwargs)
            finally:
                total_time = time_func() - start_time
                time_string = message.format(seconds=total_time,
                                             args=args, kwargs=kwargs)
                if log:
                    logger = _logging.getLogger(log) if isinstance(log, str)\
                        else _logger
                    logger.info(time_string)
                else:
                    print(time_string)
                if isinstance(append, list):
                    append.append(total_time)
        return wrapper
    return func_wrapper


def queue_it(queue=_g_queue, **put_args):
    """
    Wrapper. Instead of returning the result of the function, add it to a queue.

    .. code: python

        import reusables
        import queue

        my_queue = queue.Queue()

        @reusables.queue_it(my_queue)
        def func(a):
            return a

        func(10)

        print(my_queue.get())
        # 10


    :param queue: Queue to add result into
    """
    def func_wrapper(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            queue.put(func(*args, **kwargs), **put_args)
        return wrapper
    return func_wrapper


def log_exception(log="reusables", message="Exception in {func_name} with args:"
                                           " {args} - kwargs: {kwargs} - {err}",
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
                                                err=str(err),
                                                args=args,
                                                kwargs=kwargs))
                if exception:
                    raise exception(exception_message.format(
                        func_name=func.__name__, err=str(err)))
                raise err
        return wrapper
    return func_wrapper
