#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2019 - Chris Griffith - MIT License
from __future__ import absolute_import
import time
from threading import Lock
from functools import wraps
from collections import defaultdict
import logging
try:
    import queue as _queue
except ImportError:
    import Queue as _queue

from reusables.shared_variables import python_version, ReusablesError

__all__ = ['unique', 'time_it', 'catch_it', 'log_exception', 'retry_it',
           'lock_it', 'queue_it']

logger = logging.getLogger("reusables.wrappers")
g_lock = Lock()
g_queue = _queue.Queue()
unique_cache = defaultdict(list)


def _add_args(message, *args, **kwargs):
    if args:
        message += " - args: {args}"
    if kwargs:
        message += " - kwargs: {kwargs}"
    return message


def unique(max_retries=10, wait=0, alt_return="-no_alt_return-",
           exception=Exception, error_text=None):
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

    Message format options: {func} {args} {kwargs}

    :param max_retries: int of number of retries to attempt before failing
    :param wait: float of seconds to wait between each try, defaults to 0
    :param exception: Exception type of raise
    :param error_text: text of the exception
    :param alt_return: if specified, an exception is not raised on failure,
     instead the provided value of any type of will be returned
    """
    def func_wrap(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = (error_text if error_text else
                   "No result was unique for function '{func}'")
            if not error_text:
                msg = _add_args(msg, *args, **kwargs)
            for i in range(max_retries):
                value = func(*args, **kwargs)
                if value not in unique_cache[func.__name__]:
                    unique_cache[func.__name__].append(value)
                    return value
                if wait:
                    time.sleep(wait)
            else:
                if alt_return != "-no_alt_return-":
                    return alt_return
                raise exception(msg.format(func=func.__name__,
                                           args=args, kwargs=kwargs))
        return wrapper
    return func_wrap


def lock_it(lock=g_lock):
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
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return func_wrapper


def time_it(log=None, message=None, append=None):
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

    Message format options: {func} {seconds} {args} {kwargs}

    :param log: log as INFO level instead of printing
    :param message: string to format with total time as the only input
    :param append: list to append item too
    """
    def func_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Can't use nonlocal in 2.x
            msg = (message if message else
                   "Function '{func}' took a total of {seconds} seconds")
            if not message:
                msg = _add_args(msg, *args, **kwargs)

            time_func = (time.perf_counter if python_version >= (3, 3)
                         else time.time)
            start_time = time_func()
            try:
                return func(*args, **kwargs)
            finally:
                total_time = time_func() - start_time

                time_string = msg.format(func=func.__name__,
                                         seconds=total_time,
                                         args=args, kwargs=kwargs)
                if log:
                    my_logger = logging.getLogger(log) if isinstance(log, str)\
                                else logger
                    my_logger.info(time_string)
                else:
                    print(time_string)
                if isinstance(append, list):
                    append.append(total_time)
        return wrapper
    return func_wrapper


def queue_it(queue=g_queue, **put_args):
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
        @wraps(func)
        def wrapper(*args, **kwargs):
            queue.put(func(*args, **kwargs), **put_args)
        return wrapper
    return func_wrapper


def log_exception(log="reusables", message=None, exceptions=(Exception, ),
                  level=logging.ERROR, show_traceback=True):
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

    Message format options: {func} {err} {args} {kwargs}

    :param exceptions: types of exceptions to catch
    :param log: log name to use
    :param message: message to use in log
    :param level: logging level
    :param show_traceback: include full traceback or just error message
    """
    def func_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = message if message else "Exception in '{func}': {err}"
            if not message:
                msg = _add_args(msg, *args, **kwargs)

            try:
                return func(*args, **kwargs)
            except exceptions as err:
                my_logger = (logging.getLogger(log) if isinstance(log, str)
                             else log)
                my_logger.log(level, msg.format(func=func.__name__,
                                                err=str(err),
                                                args=args, kwargs=kwargs),
                              exc_info=show_traceback)
                raise err
        return wrapper
    return func_wrapper


def catch_it(exceptions=(Exception, ), default=None, handler=None):
    """
    If the function encounters an exception, catch it, and
    return the specified default or sent to a handler function instead.

    .. code :: python

        def handle_error(exception, func, *args, **kwargs):
            print(f"{func.__name__} raised {exception} when called with {args}")

        @reusables.catch_it(handler=err_func)
        def will_raise(message="Hello")
            raise Exception(message)


    :param exceptions: tuple of exceptions to catch
    :param default: what to return if the exception is caught
    :param handler: function to send exception, func, *args and **kwargs
    """
    def func_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as err:
                if handler:
                    return handler(err, func, *args, **kwargs)
                return default
        return wrapper
    return func_wrapper


def retry_it(exceptions=(Exception, ), tries=10, wait=0, handler=None,
             raised_exception=ReusablesError, raised_message=None):
    """
    Retry a function if an exception is raised, or if output_check returns
    False.

    Message format options: {func} {args} {kwargs}

    :param exceptions: tuple of exceptions to catch
    :param tries: number of tries to retry the function
    :param wait: time to wait between executions in seconds
    :param handler: function to check if output is valid, must return bool 
    :param raised_exception: default is ReusablesError
    :param raised_message: message to pass to raised exception
    """
    def func_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = (raised_message if raised_message
                   else "Max retries exceeded for function '{func}'")
            if not raised_message:
                msg = _add_args(msg, *args, **kwargs)
            try:
                result = func(*args, **kwargs)
            except exceptions:
                if tries:
                    if wait:
                        time.sleep(wait)
                    return retry_it(exceptions=exceptions, tries=tries-1,
                                    handler=handler,
                                    wait=wait)(func)(*args, **kwargs)
                if raised_exception:
                    exc = raised_exception(msg.format(func=func.__name__,
                                           args=args, kwargs=kwargs))
                    exc.__cause__ = None
                    raise exc
            else:
                if handler:
                    if not handler(result):
                        return retry_it(exceptions=exceptions, tries=tries - 1,
                                        handler=handler,
                                        wait=wait)(func)(*args, **kwargs)
                return result
        return wrapper
    return func_wrapper

