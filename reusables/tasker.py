#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2019 - Chris Griffith - MIT License
try:
    import queue as queue
except ImportError:
    import Queue as queue
import multiprocessing as mp
import uuid
import time
import logging
import datetime

from reusables.shared_variables import win_based

__all__ = ['Tasker']


class Tasker(object):
    """
    An advanced multiprocessing pool, designed to run in the background,
    with ability to change number of workers or pause the service all together.

    Simply subclass Tasker, overwrite `perform_task` and `run`!

    It has in and out queues (task_queue, result_queue) which can be provided
    or will automatically be created as `multiprocessing.Queue()`s.

    .. warning::

        Use multiprocessing.Queue not queue.Queue

    .. warning::

        Do not use on Windows at this time

    :param tasks: list of tasks to pre-populate the queue with
    :param max_tasks: the max number of parallel workers
    :param task_timeout: how long can each task take
    :param task_queue: option to specify an existing queue of tasks
    :param result_queue: option to specify an existing queue for results
    :param run_until: datetime to run until
    """

    def __init__(self, tasks=(), max_tasks=4, task_timeout=None,
                 task_queue=None, result_queue=None, command_queue=None,
                 run_until=None, logger='reusables', **task_kwargs):
        if logger:
            self.log = logging.getLogger('reusables')
        self.task_queue = task_queue or mp.Queue()
        if tasks:
            for task in tasks:
                self.task_queue.put(task)
        self.result_queue = result_queue or mp.Queue()
        self.command_queue = command_queue or mp.Queue()
        self.free_tasks = [str(uuid.uuid4()) for _ in range(max_tasks)]
        self.current_tasks = {}
        for task_id in self.free_tasks:
            self.current_tasks[task_id] = {}
        self.busy_tasks = []
        self.max_tasks = max_tasks
        self.timeout = task_timeout
        self.run_until = run_until
        self._pause, self._end = mp.Value('b', False), mp.Value('b', False)
        self.background_process = None
        self.task_kwargs = task_kwargs

    def get(self, timeout=None):
        """Retrieve next result from the queue"""
        return self.result_queue.get(timeout=timeout)

    def put(self, task):
        """Add a task to be processed to the queue"""
        return self.task_queue.put(task)

    @staticmethod
    def perform_task(task, result_queue, **kwargs):
        """Function to be overwritten that performs the tasks from the list"""
        raise NotImplementedError()

    def _update_tasks(self):
        still_busy = []
        for task_id in self.busy_tasks:
            if not self.current_tasks[task_id]:
                self.free_tasks.append(task_id)
            elif not self.current_tasks[task_id]['proc'].is_alive():
                self.free_tasks.append(task_id)
            elif self.timeout and (self.current_tasks[task_id]['start'] +
                                   self.timeout) < time.time():
                try:
                    self.current_tasks[task_id]['proc'].terminate()
                except Exception as err:
                    self.log.exception("Error while terminating "
                                       "task {} - {}".format(task_id, err))
                self.free_tasks.append(task_id)
            else:
                still_busy.append(task_id)
        self.busy_tasks = still_busy

    def _free_task(self):
        if self.free_tasks:
            task_id = self.free_tasks.pop(0)
            self.busy_tasks.append(task_id)
            return task_id
        else:
            return False

    def _return_task(self, task_id):
        self.free_tasks.append(task_id)
        self.busy_tasks.remove(task_id)

    def _start_task(self, task_id, task):
        self.current_tasks[task_id]['proc'] = mp.Process(
            target=self.perform_task, args=(task, self.result_queue),
            kwargs=self.task_kwargs)
        self.current_tasks[task_id]['start_time'] = time.time()
        self.current_tasks[task_id]['proc'].start()

    def _reset_and_pause(self):
        self.current_tasks = {}
        self.free_tasks = []
        self.busy_tasks = []
        self._pause.value = True

    def change_task_size(self, size):
        """Blocking request to change number of running tasks"""
        self._pause.value = True
        self.log.debug("About to change task size to {0}".format(size))
        try:
            size = int(size)
        except ValueError:
            self.log.error("Cannot change task size, non integer size provided")
            return False
        if size < 0:
            self.log.error("Cannot change task size, less than 0 size provided")
            return False
        self.max_tasks = size
        if size < self.max_tasks:
            diff = self.max_tasks - size
            self.log.debug("Reducing size offset by {0}".format(diff))
            while True:
                self._update_tasks()
                if len(self.free_tasks) >= diff:
                    for i in range(diff):
                        task_id = self.free_tasks.pop(0)
                        del self.current_tasks[task_id]
                    break
                time.sleep(0.5)
            if not size:
                self._reset_and_pause()
                return True
        elif size > self.max_tasks:
            diff = size - self.max_tasks
            for i in range(diff):
                task_id = str(uuid.uuid4())
                self.current_tasks[task_id] = {}
                self.free_tasks.append(task_id)
        self._pause.value = False
        self.log.debug("Task size changed to {0}".format(size))
        return True

    def stop(self):
        """Hard stop the server and sub process"""
        self._end.value = True
        if self.background_process:
            try:
                self.background_process.terminate()
            except Exception:
                pass
        for task_id, values in self.current_tasks.items():
            try:
                values['proc'].terminate()
            except Exception:
                pass

    def pause(self):
        """Stop any more tasks from being run"""
        self._pause.value = True

    def unpuase(self):
        """Allows tasks to be run again"""
        self._pause.value = False

    def get_state(self):
        """Get general information about the state of the class"""
        return {"started": (True if self.background_process and
                            self.background_process.is_alive() else False),
                "paused": self._pause.value,
                "stopped": self._end.value,
                "tasks": len(self.current_tasks),
                "busy_tasks": len(self.busy_tasks),
                "free_tasks": len(self.free_tasks)}

    def _check_command_queue(self):
        try:
            cmd = self.command_queue.get(block=False)
        except queue.Empty:
            return

        if "stop" in cmd.lower():
            self.stop()
        elif "pause" in cmd.lower():
            self.pause()
        elif "unpause" in cmd.lower():
            self.unpuase()
        elif "change task size" in cmd.lower():
            try:
                new_size = int(cmd.split(" ")[-1])
            except Exception as err:
                self.log.warning("Received improperly formatted command tasking"
                                 " '{0}' - {1}".format(cmd, err))
            else:
                self.change_task_size(new_size)
        else:
            self.log.warning("Received an unknown command '{0}'".format(cmd))

    def hook_pre_command(self):
        pass

    def hook_post_command(self):
        pass

    def hook_pre_task(self):
        pass

    def hook_post_task(self):
        pass

    def main_loop(self, stop_at_empty=False):
        """Blocking function that can be run directly, if so would probably
        want to specify 'stop_at_empty' to true, or have a separate process
        adding items to the queue. """
        try:
            while True:
                self.hook_pre_command()
                self._check_command_queue()
                if self.run_until and self.run_until < datetime.datetime.now():
                    self.log.info("Time limit reached")
                    break
                if self._end.value:
                    break
                if self._pause.value:
                    time.sleep(.5)
                    continue
                self.hook_post_command()
                self._update_tasks()
                task_id = self._free_task()
                if task_id:
                    try:
                        task = self.task_queue.get(timeout=.1)
                    except queue.Empty:
                        if stop_at_empty:
                            break
                        self._return_task(task_id)
                    else:
                        self.hook_pre_task()
                        self.log.debug("Starting task on {0}".format(task_id))
                        try:
                            self._start_task(task_id, task)
                        except Exception as err:
                            self.log.exception("Could not start task {0} -"
                                               " {1}".format(task_id, err))
                        else:
                            self.hook_post_task()
        finally:
            self.log.info("Ending main loop")

    def run(self):
        """Start the main loop as a background process. *nix only"""
        if win_based:
            raise NotImplementedError("Please run main_loop, "
                                      "backgrounding not supported on Windows")
        self.background_process = mp.Process(target=self.main_loop)
        self.background_process.start()
