#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import queue as _queue
except ImportError:
    import Queue as _queue
import multiprocessing as _mp
import uuid as _uuid
import time as _time
import logging as _logging

log = _logging.getLogger('reusables.tasker')
#TODO make logger multiprocessing safe


class Tasker(object):

    def __init__(self, max_tasks=2, task_timeout=None):
        self.task_queue = _mp.Queue()
        self.command_queue = _mp.Queue()
        self.free_tasks = [_uuid.uuid4() for _ in range(max_tasks)]
        self.current_tasks = {task_id: {} for task_id in self.free_tasks}
        self.busy_tasks = []
        self.max_tasks = max_tasks
        self.timeout = task_timeout
        self.pause, self.end = False, False
        self._internal_code_check = self.perform_task.__code__
        self.background_process = None

    def perform_task(self):
        raise NotImplementedError()

    def _update_tasks(self):
        still_busy = []
        for task_id in self.busy_tasks:
            if not self.current_tasks[task_id]:
                self.free_tasks.append(task_id)
            elif not self.current_tasks[task_id]['proc'].is_alive():
                self.free_tasks.append(task_id)
            elif self.timeout and (self.current_tasks[task_id]['start'] +
                                   self.timeout) < _time.time():
                try:
                    self.current_tasks[task_id]['proc'].terminate()
                except Exception as err:
                    log.exception("Error while terminating "
                                  "task {} - {}".format(task_id, err))
                self.free_tasks.append(task_id)
            else:
                still_busy.append(task_id)
        self.busy_nodes = still_busy

    def _free_task(self):
        if self.free_tasks:
            task_id = self.free_tasks.pop(0)
            self.busy_nodes.append(task_id)
            return task_id
        else:
            return False

    def _return_task(self, task_id):
        self.free_tasks.append(task_id)
        self.busy_tasks.remove(task_id)

    def _start_task(self, task_id, task):
        self.current_tasks[task_id]['proc'] = _mp.Process(
            target=self.perform_task, args=(task, ))
        self.current_tasks[task_id]['start_time'] = _time.time()
        self.current_tasks[task_id]['proc'].start()

    def _reset_and_pause(self):
        self.current_tasks = {}
        self.free_tasks = []
        self.busy_tasks = []
        self.pause = True

    def change_task_size(self, size):
        """Blocking request to change number of running tasks"""
        try:
            size = int(size)
        except ValueError:
            log.error("Someone provided a non integer size")
        if size < 0:
            log.error("Someone provided a less than 0 size")
            return
        if size < self.max_tasks:
            diff = self.max_tasks - size
            while True:
                self._update_tasks()
                if len(self.free_tasks) >= diff:
                    for i in range(diff):
                        task_id = self.free_tasks.pop(0)
                        del self.current_tasks[task_id]
                _time.sleep(0.5)
            if not size:
                self._reset_and_pause()

        elif size > self.max_tasks:
            diff = size - self.max_tasks
            self.max_tasks = size
            for i in range(diff):
                task_id = _uuid.uuid4()
                self.current_tasks[task_id] = {}
                self.free_tasks.append(task_id)
        self.pause = False

    def stop(self):
        self.end = True
        self.change_task_size(0)
        if self.background_process:
            try:
                self.background_process.terminate()
            except Exception:
                pass

    def _perform_command(self, timeout=None):
        command = self.command_queue.get(timeout=timeout)
        if 'task' not in command:
            log.error("Malformed command: {}".format(command))
        elif command['command'] == 'max_tasks':
            self.change_task_size(command['value'])
        elif command['command'] == 'pause':
            self.pause = True
        elif command['command'] == 'unpuase':
            self.pause = False
        elif command['command'] == 'stop':
            self.stop()

    def run(self):
        if self._internal_code_check == self.perform_task.__code__:
            raise Exception("Tasker requires you to overwrite "
                            "the 'perform_task' method")
        while True:
            if self.end:
                break
            if self.pause:
                self._perform_command()
                continue
            self._update_tasks()
            task_id = self._free_task()
            if task_id:
                try:
                    task = self.task_queue.get(timeout=.1)
                except _queue.Empty:
                    self._return_task(task_id)
                else:
                    self._start_task(task_id, task)
            self._perform_command(timeout=.1)

    def run_in_background(self):
        self.background_process = _mp.Process(target=self.run)
        self.background_process.start()
