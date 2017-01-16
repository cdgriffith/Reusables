#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import reusables
import logging
import platform

from .common_test_data import *

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


class TestTasker(BaseTestClass):

    def test_example_add_tasker(self):
        if reusables.win_based:
            return
        tasker = ExampleAddTasker(list(range(100)))
        try:
            tasker.run()
            tasker.change_task_size(2)
            tasker.change_task_size(6)
            tasker.pause()
            tasker.unpuase()
            assert isinstance(tasker.get_state(), dict)
            results = [tasker.result_queue.get() for _ in range(100)]
        finally:
            tasker.stop()

        assert len(results) == 100

    def test_stop_at_emtpy(self):
        tasker = ExampleSleepTasker([.1, .2])
        tasker.main_loop(True)
        assert [tasker.result_queue.get() for _ in (0, 0)] == [.1, .2]

    def test_bad_size_change(self):
        tasker = reusables.Tasker()
        try:
            tasker.perform_task(1,2)
        except NotImplementedError:
            pass
        else:
            assert False

        assert not tasker.change_task_size(-1)
        assert not tasker.change_task_size('a')
        assert tasker.change_task_size(2)
        assert tasker.change_task_size(6)
        tasker._reset_and_pause()

    def test_tasker_commands(self):
        import datetime
        reusables.add_stream_handler("reusables")
        tasker = ExampleAddTasker(max_tasks=4, run_until=datetime.datetime.now() + datetime.timedelta(minutes=1))
        tasker.command_queue.put("change task size 1")
        tasker.command_queue.put("pause")
        tasker.command_queue.put("unpause")
        tasker.command_queue.put("stop")
        tasker.put(5)
        tasker.main_loop()
        r = tasker.get_state()
        assert r['stopped'], r
        assert tasker.max_tasks == 1, tasker.max_tasks


class TestPool(unittest.TestCase):

    def test_run_in_pool(self):
        def test(a, b=True):
            return a, a * 2, b

        res = reusables.run_in_pool(test, [1, 2, 3, 4])
        assert res == [(1, 2, True), (2, 4, True), (3, 6, True), (4, 8, True)]

        res2 = reusables.run_in_pool(test, [4, 6], target_kwargs={"b": False})
        assert res2 == [(4, 8, False), (6, 12, False)]

