#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import queue as _queue
except ImportError:
    import Queue as _queue
import multiprocessing as _mp
import multiprocessing.pool as _pool
import uuid as _uuid
import time as _time
import logging as _logging
from functools import partial as _partial

_logger = _logging.getLogger('reusables.tasker')
#TODO make logger multiprocessing safe


class Tasker(object):

    def __init__(self, tasks=(), max_tasks=4, task_timeout=None):
        self.task_queue = _mp.Queue()
        if tasks:
            for task in tasks:
                self.task_queue.put(task)
        self.command_queue = _mp.Queue()
        self.result_queue = _mp.Queue()
        self.free_tasks = [str(_uuid.uuid4()) for _ in range(max_tasks)]
        self.current_tasks = {}
        for task_id in self.free_tasks:
            self.current_tasks[task_id] = {}
        self.busy_tasks = []
        self.max_tasks = max_tasks
        self.timeout = task_timeout
        self._pause, self._end = _mp.Value('b', False), _mp.Value('b', False)
        self.background_process = None

    @staticmethod
    def perform_task(task, queue):
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
                    _logger.exception("Error while terminating "
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
        self.current_tasks[task_id]['proc'] = _mp.Process(
            target=self.perform_task, args=(task, self.result_queue))
        self.current_tasks[task_id]['start_time'] = _time.time()
        self.current_tasks[task_id]['proc'].start()

    def _reset_and_pause(self):
        self.current_tasks = {}
        self.free_tasks = []
        self.busy_tasks = []
        self._pause.value = True

    def change_task_size(self, size):
        """Blocking request to change number of running tasks"""
        self._pause.value = True
        _logger.debug("About to change task size to {0}".format(size))
        try:
            size = int(size)
        except ValueError:
            _logger.error("Cannot change task size, non integer size provided")
            return
        if size < 0:
            _logger.error("Cannot change task size, less than 0 size provided")
            return
        if size < self.max_tasks:
            diff = self.max_tasks - size
            _logger.debug("Reducing size offset by {0}".format(diff))
            while True:
                self._update_tasks()
                if len(self.free_tasks) >= diff:
                    for i in range(diff):
                        task_id = self.free_tasks.pop(0)
                        del self.current_tasks[task_id]
                    break
                _time.sleep(0.5)
            if not size:
                self._reset_and_pause()

        elif size > self.max_tasks:
            diff = size - self.max_tasks
            self.max_tasks = size
            for i in range(diff):
                task_id = str(_uuid.uuid4())
                self.current_tasks[task_id] = {}
                self.free_tasks.append(task_id)
        self._pause.value = False
        _logger.debug("Task size changed to {0}".format(size))

    def stop(self):
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
        self._pause.value = True

    def unpuase(self):
        self._pause.value = False

    def get_state(self):
        return {"started": (True if self.background_process and
                            self.background_process.is_alive() else False),
                "paused": self._pause.value,
                "stopped": self._end.value,
                "tasks": len(self.current_tasks),
                "busy_tasks": len(self.busy_tasks),
                "free_tasks": len(self.free_tasks)}

    def main_loop(self, stop_at_empty=False):
        while True:
            if self._end.value:
                break
            if self._pause.value:
                _time.sleep(.5)
                continue
            self._update_tasks()
            task_id = self._free_task()
            if task_id:
                try:
                    task = self.task_queue.get(timeout=.1)
                except _queue.Empty:
                    if stop_at_empty:
                        break
                    self._return_task(task_id)
                else:
                    _logger.debug("Starting task on {0}".format(task_id))
                    try:
                        self._start_task(task_id, task)
                    except Exception as err:
                        _logger.exception("Could not start task {0} -"
                                          " {1}".format(task_id, err))

    def run(self):
        self.background_process = _mp.Process(target=self.main_loop)
        self.background_process.start()


def run_in_pool(target, iterable, threaded=True, processes=4,
                async=False, target_kwargs=None):
    """ Run a set of iterables to a function in a Threaded or MP Pool

    :param target: function to run
    :param iterable: positional arg to pass to function
    :param threaded: Threaded if True Multiprocessed if False
    :param processes: Number of workers
    :param async: will do map_async if True
    :param target_kwargs: Keyword arguments to set on the function as a partial
    :return: pool results
    """
    pool = _pool.ThreadPool if threaded else _pool.Pool

    if target_kwargs:
        target = _partial(target, **target_kwargs if target_kwargs else None)

    p = pool(processes)
    try:
        results = (p.map_async(target, iterable) if async
                   else p.map(target, iterable))
    finally:
        p.close()
        p.join()
    return results
