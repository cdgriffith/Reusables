#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import os
import time
import shutil
import tarfile
import tempfile
import reusables
import subprocess
import logging

log = reusables.get_logger()


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

    @unittest.skip
    def test_example_add_tasker(self):
        tasker = ExampleAddTasker(list(range(100)))
        log.info("about to start")
        tasker.run_in_background()
        log.info(tasker.get_state())
        time.sleep(2)
        tasker.stop()
        while True:
            log.info(tasker.result_queue.get())


class TestPool(unittest.TestCase):

    def test_run_in_pool(self):
        def test(a, b=True):
            return a, a * 2, b

        res = reusables.run_in_pool(test, [1, 2, 3, 4])
        assert res == [(1, 2, True), (2, 4, True), (3, 6, True), (4, 8, True)]

        res2 = reusables.run_in_pool(test, [4, 6], target_kwargs={"b": False})
        assert res2 == [(4, 8, False), (6, 12, False)]

