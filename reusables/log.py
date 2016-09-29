#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2016 - Chris Griffith - MIT License
"""
Logging helper functions and common log formats.
"""
import logging as _logging
import sys as _sys

log_common_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_level_first_format = '%(levelname)s - %(name)s - %(asctime)s - %(message)s'
log_threaded_format = '%(relativeCreated)d %(threadName)s : %(message)s'
log_easy_read_format = '%(asctime)s - %(name)-12s  %(levelname)-8s ' \
                       ' %(message)s'
log_easy_thread_format = '%(relativeCreated)8d %(threadName)s : %(name)-12s ' \
                         ' %(levelname)-8s  %(message)s'
log_detailed_format = '%(asctime)s : %(relativeCreated)5d %(threadName)s : ' \
                      '%(name)s %(levelname)s %(message)s'

if _sys.version_info < (2, 7):
    class NullHandler(_logging.Handler):
        def emit(self, record):
            pass

    _logging.NullHandler = NullHandler


def get_stream_handler(stream=_sys.stderr, level=_logging.INFO,
                       log_format=log_easy_read_format):
    """
    Returns a set up stream handler to add to a logger.

    :param stream: which stream to use, defaults to sys.stderr
    :param level: logging level to set handler at
    :param log_format: formatter to use
    :return: stream handler
    """
    sh = _logging.StreamHandler(stream)
    sh.setLevel(level)
    sh.setFormatter(_logging.Formatter(log_format))
    return sh


def get_file_handler(file_path="out.log", level=_logging.INFO,
                     log_format=log_easy_read_format):
    """
    Set up a file handler to add to a logger.

    :param file_path: file to write the log to
    :param level: logging level to set handler at
    :param log_format: formatter to use
    :return: file handler
    """
    fh = _logging.FileHandler(file_path)
    fh.setLevel(level)
    fh.setFormatter(_logging.Formatter(log_format))
    return fh


def get_logger(module_name=__name__, level=_logging.INFO, stream=_sys.stderr,
               file_path=None, log_format=log_easy_read_format,
               suppress_warning=True, ignore_existing=False):
    """
    Grabs the specified logger and adds wanted handlers to it. Will
    default to adding a stream handler.

    :param module_name: logger name to use
    :param level: logging level to set logger at
    :param stream: stream to log to, or None
    :param file_path: file path to log to, or None
    :param log_format: format to set the handlers to use
    :param suppress_warning: add a NullHandler if no other handler is specified
    :return: configured logger
    """
    new_logger = _logging.getLogger(module_name)

    if stream and not new_logger.handlers:
        new_logger.addHandler(get_stream_handler(stream, level, log_format))
    elif not file_path and suppress_warning and not new_logger.handlers:
            new_logger.addHandler(_logging.NullHandler())

    if file_path:
        new_logger.addHandler(get_file_handler(file_path, level, log_format))
    if level > 0:
        new_logger.setLevel(level)
    return new_logger


def remove_stream_handlers(logger):
    """
    Remove only stream handlers from the specified logger

    :param logger: logging object to modify
    :return: streamless logger
    """
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
    """
    Remove only file handlers from the specified logger. Will go through
    and close each handler for safety.

    :param logger: logging object to modify
    :return: fileless logger
    """
    new_handlers = []
    for handler in logger.handlers:
        if isinstance(handler, _logging.FileHandler):
            handler.close()
        else:
            new_handlers.append(handler)
    logger.handlers = new_handlers


def remove_all_handlers(logger):
    """
    Safely remove all handlers from the logger

    :param logger: logging object to modify
    :return: handle-less logger
    """
    remove_file_handlers(logger)
    logger.handlers = []


def change_logger_levels(logger, level=_logging.DEBUG):
    """
    Go through the logger and handlers and update their levels to the
    one specified.

    :param logger: logging object to modify
    :param level: logging level to set at (10=Debug, 20=Info, 30=Warn, 40=Error)
    :return:
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.level = level
