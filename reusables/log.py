#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Logging helper functions and common log formats.

Part of the Reusables package.

Copyright (c) 2014-2016 - Chris Griffith - MIT License
"""
import logging as _logging
import sys

log_common_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_level_first_format = '%(levelname)s - %(name)s - %(asctime)s - %(message)s'
log_threaded_format = '%(relativeCreated)6d %(threadName)s %(message)s'
log_easy_read_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
log_easy_thread_format = '%(relativeCreated)5d %(name)-12s ' \
                         '%(levelname)-8s %(message)s'
log_detailed_format = '%(asctime)s : %(relativeCreated)5d %(threadName)s : ' \
                      '%(name)s %(levelname)s %(message)s'


def get_stream_handler(stream=sys.stderr, level=_logging.INFO,
                       log_format=log_easy_read_format):

    sh = _logging.StreamHandler(stream)
    sh.setLevel(level)
    sh.setFormatter(_logging.Formatter(log_format))
    return sh


def get_file_handler(file_path="out.log", level=_logging.INFO,
                     log_format=log_easy_read_format):

    fh = _logging.FileHandler(file_path)
    fh.setLevel(level)
    fh.setFormatter(_logging.Formatter(log_format))
    return fh


def get_logger(module_name=__name__, level=_logging.INFO, stream=sys.stderr,
               file_path=None, log_format=log_easy_read_format,
               suppress_warning=True):

    new_logger = _logging.getLogger(module_name)
    if stream:
        new_logger.addHandler(get_stream_handler(stream, level, log_format))
    elif not file_path and suppress_warning:
            new_logger.addHandler(_logging.NullHandler())

    if file_path:
        new_logger.addHandler(get_file_handler(file_path, level, log_format))
    if level > 0:
        new_logger.setLevel(level)
    return new_logger


def remove_stream_handlers(logger):
    new_handlers = []
    for handler in logger.handlers:
        # FileHandler is a subclass of StreamHandler so
        # 'if not a StreamHandler' does not work
        if (isinstance(handler, _logging.FileHandler) or
            isinstance(handler, _logging.NullHandler) or
            (isinstance(handler, _logging.Handler) and not
                isinstance(handler, _logging.StreamHandler))):
            new_handlers.append(handler)
    logger.handlers = new_handlers


def remove_file_handlers(logger):
    new_handlers = []
    for handler in logger.handlers:
        if isinstance(handler, _logging.FileHandler):
            try:
                handler.close()
            except Exception:
                pass
        else:
            new_handlers.append(handler)
    logger.handlers = new_handlers


def remove_all_handlers(logger):
    logger.handlers = []

