#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import time
import reusables
import logging

reusables.change_logger_levels(logging.getLogger('reusables'), logging.INFO)


class ExampleSleepTasker(reusables.Tasker):

    @staticmethod
    def perform_task(task, queue):
        time.sleep(task)
        queue.put(task)


class ExampleAddTasker(reusables.Tasker):

    @staticmethod
    def perform_task(task, queue):
        queue.put(task, task + task)


class TestTasker(unittest.TestCase):

    def test_example_add_tasker(self):
        tasker = ExampleAddTasker(list(range(100)))
        try:
            tasker.run()
            tasker.change_task_size(2)
            tasker.change_task_size(6)
            tasker.pause()
            tasker.unpuase()
            results = [tasker.result_queue.get() for _ in range(100)]
        finally:
            tasker.stop()

        assert len(results) == 100

    def test_stop_at_emtpy(self):
        tasker = ExampleSleepTasker([.1, .2])
        tasker.main_loop(True)
        assert [tasker.result_queue.get() for _ in (0, 0)] == [.1, .2]


class TestPool(unittest.TestCase):

    def test_run_in_pool(self):
        def test(a, b=True):
            return a, a * 2, b

        res = reusables.run_in_pool(test, [1, 2, 3, 4])
        assert res == [(1, 2, True), (2, 4, True), (3, 6, True), (4, 8, True)]

        res2 = reusables.run_in_pool(test, [4, 6], target_kwargs={"b": False})
        assert res2 == [(4, 8, False), (6, 12, False)]

