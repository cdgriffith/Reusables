#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os

from .common_test_data import *

from reusables import unique, lock_it, time_it, queue_it, get_logger, \
    log_exception, remove_file_handlers


@unique(exception=OSError, error_text="WHY ME!")
def unique_function_1(a):
    return a


@unique(alt_return=33)
def unique_function_2(a):
    return a


@unique(wait=1)
def unique_function_3():
    return int(time.time())


class TestWrappers(BaseTestClass):


    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink("out.log")
        except OSError:
            pass

    def test_unique(self):
        unique_function_1(1)
        unique_function_2(1)
        try:
            unique_function_1(1)
        except OSError as err:
            assert "WHY ME!" in str(err)

        assert unique_function_2(1) == 33

        a = unique_function_3()
        b = unique_function_3()
        c = unique_function_3()

        assert c > b > a

    def test_locker(self):
        import threading

        @lock_it()
        def func1():
            import time
            time.sleep(2)

        start = time.time()
        a = threading.Thread(target=func1)
        b = threading.Thread(target=func1)
        a.daemon = False
        b.daemon = False
        a.start()
        b.start()
        a.join()
        b.join()
        assert (time.time() - start) > 3

    def test_time(self):
        my_list = []

        @time_it(append=my_list)
        def func():
            return 5 + 3

        @time_it(log=True)
        def func2():
            return 7 + 3

        func()
        func2()

        assert len(my_list) == 1
        assert isinstance(my_list[0], float)

    def test_queue(self):
        try:
            import queue
        except ImportError:
            import Queue as queue

        q = queue.Queue()

        @queue_it(q)
        def func():
            return 5 + 3

        func()

        assert q.get() == 8

    def test_log_exception(self):
        """
        Validate the custom log exception is raised correctly.
        """
        @log_exception()
        def unique_function_4():
            raise Exception("Bad")

        try:
            unique_function_4()
        except Exception as err:
            assert "Bad" in str(err)

    def test_log_exception_message(self):
        """
        Validate the message passed to the custom log exception is written
        correctly in the logs.
        """
        get_logger("my_logger", file_path="out.log")
        message = "I would like to take this moment to say something " \
                  "interesting has happened. "

        @log_exception("my_logger", message=message)
        def unique_function_5():
            raise Exception("Interesting")

        try:
            unique_function_5()
        except Exception:
            pass

        remove_file_handlers("my_logger")

        with open(os.path.join("out.log"), "r") as f:
            assert message in f.readlines()[0]

        os.remove(os.path.join("out.log"))

if __name__ == "__main__":
    unittest.main()
