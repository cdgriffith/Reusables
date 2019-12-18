#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2019 - Chris Griffith - MIT License
"""
Logging helper functions and common log formats.
"""
from __future__ import absolute_import
import warnings
import logging
import sys
from logging.handlers import (RotatingFileHandler,
                              TimedRotatingFileHandler)

from reusables.namespace import Namespace
from reusables.shared_variables import sizes

__all__ = ['log_formats', 'get_logger', 'setup_logger', 'get_registered_loggers',
           'get_file_handler', 'get_stream_handler', 'add_file_handler',
           'add_stream_handler', 'add_rotating_file_handler',
           'add_timed_rotating_file_handler', 'change_logger_levels',
           'remove_all_handlers', 'remove_file_handlers',
           'remove_stream_handlers', 'setup_logger']

log_formats = Namespace({
    'common': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'level_first': '%(levelname)s - %(name)s - %(asctime)s - %(message)s',
    'threaded': '%(relativeCreated)d %(threadName)s : %(message)s',
    'easy_read': '%(asctime)s - %(name)-12s  %(levelname)-8s %(message)s',
    'easy_thread': '%(relativeCreated)8d %(threadName)s : %(name)-12s '
                   '%(levelname)-8s  %(message)s',
    'detailed': '%(asctime)s : %(relativeCreated)5d %(threadName)s : %(name)s '
                '%(levelname)s %(message)s'
})

if sys.version_info < (2, 7):
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

    logging.NullHandler = NullHandler


def get_logger(*args, **kwargs):
    """ Depreciated, use setup_logger"""
    warnings.warn("get_logger is changing name to setup_logger",
                  DeprecationWarning)
    return setup_logger(*args, **kwargs)


def get_stream_handler(stream=sys.stderr, level=logging.INFO,
                       log_format=log_formats.easy_read):
    """
    Returns a set up stream handler to add to a logger.

    :param stream: which stream to use, defaults to sys.stderr
    :param level: logging level to set handler at
    :param log_format: formatter to use
    :return: stream handler
    """
    sh = logging.StreamHandler(stream)
    sh.setLevel(level)
    sh.setFormatter(logging.Formatter(log_format))
    return sh


def get_file_handler(file_path="out.log", level=logging.INFO,
                     log_format=log_formats.easy_read,
                     handler=logging.FileHandler,
                     **handler_kwargs):
    """
    Set up a file handler to add to a logger.

    :param file_path: file to write the log to, defaults to out.log
    :param level: logging level to set handler at
    :param log_format: formatter to use
    :param handler: logging handler to use, defaults to FileHandler
    :param handler_kwargs: options to pass to the handler
    :return: handler
    """
    fh = handler(file_path, **handler_kwargs)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(log_format))
    return fh


def setup_logger(module_name=None, level=logging.INFO, stream=sys.stderr,
                 file_path=None, log_format=log_formats.easy_read,
                 suppress_warning=True):
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
    new_logger = logging.getLogger(module_name)

    if stream:
        new_logger.addHandler(get_stream_handler(stream, level, log_format))
    elif not file_path and suppress_warning and not new_logger.handlers:
            new_logger.addHandler(logging.NullHandler())

    if file_path:
        new_logger.addHandler(get_file_handler(file_path, level, log_format))
    if level > 0:
        new_logger.setLevel(level)
    return new_logger


def add_stream_handler(logger=None, stream=sys.stderr, level=logging.INFO,
                       log_format=log_formats.easy_read):
    """
    Addes a newly created stream handler to the specified logger

    :param logger: logging name or object to modify, defaults to root logger
    :param stream: which stream to use, defaults to sys.stderr
    :param level: logging level to set handler at
    :param log_format: formatter to use
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.addHandler(get_stream_handler(stream, level, log_format))


def add_file_handler(logger=None, file_path="out.log", level=logging.INFO,
                     log_format=log_formats.easy_read):
    """
    Addes a newly created file handler to the specified logger

    :param logger: logging name or object to modify, defaults to root logger
    :param file_path: path to file to log to
    :param level: logging level to set handler at
    :param log_format: formatter to use
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.addHandler(get_file_handler(file_path, level, log_format))


def add_rotating_file_handler(logger=None, file_path="out.log",
                              level=logging.INFO,
                              log_format=log_formats.easy_read,
                              max_bytes=10*sizes.mb, backup_count=5,
                              **handler_kwargs):
    """ Adds a rotating file handler to the specified logger.

    :param logger: logging name or object to modify, defaults to root logger
    :param file_path: path to file to log to
    :param level: logging level to set handler at
    :param log_format: log formatter
    :param max_bytes: Max file size in bytes before rotating
    :param backup_count: Number of backup files
    :param handler_kwargs: options to pass to the handler
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.addHandler(get_file_handler(file_path, level, log_format,
                                       handler=RotatingFileHandler,
                                       maxBytes=max_bytes,
                                       backupCount=backup_count,
                                       **handler_kwargs))


def add_timed_rotating_file_handler(logger=None, file_path="out.log",
                                    level=logging.INFO,
                                    log_format=log_formats.easy_read,
                                    when='w0', interval=1, backup_count=5,
                                    **handler_kwargs):
    """ Adds a timed rotating file handler to the specified logger.
    Defaults to weekly rotation, with 5 backups.

    :param logger: logging name or object to modify, defaults to root logger
    :param file_path: path to file to log to
    :param level: logging level to set handler at
    :param log_format: log formatter
    :param when:
    :param interval:
    :param backup_count: Number of backup files
    :param handler_kwargs: options to pass to the handler
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.addHandler(get_file_handler(file_path, level, log_format,
                                       handler=TimedRotatingFileHandler,
                                       when=when,
                                       interval=interval,
                                       backupCount=backup_count,
                                       **handler_kwargs))


def remove_stream_handlers(logger=None):
    """
    Remove only stream handlers from the specified logger

    :param logger: logging name or object to modify, defaults to root logger
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    new_handlers = []
    for handler in logger.handlers:
        # FileHandler is a subclass of StreamHandler so
        # 'if not a StreamHandler' does not work
        if (isinstance(handler, logging.FileHandler) or
            isinstance(handler, logging.NullHandler) or
            (isinstance(handler, logging.Handler) and not
                isinstance(handler, logging.StreamHandler))):
            new_handlers.append(handler)
    logger.handlers = new_handlers


def remove_file_handlers(logger=None):
    """
    Remove only file handlers from the specified logger. Will go through
    and close each handler for safety.

    :param logger: logging name or object to modify, defaults to root logger
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    new_handlers = []
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
        else:
            new_handlers.append(handler)
    logger.handlers = new_handlers


def remove_all_handlers(logger=None):
    """
    Safely remove all handlers from the logger

    :param logger: logging name or object to modify, defaults to root logger
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    remove_file_handlers(logger)
    logger.handlers = []


def change_logger_levels(logger=None, level=logging.DEBUG):
    """
    Go through the logger and handlers and update their levels to the
    one specified.

    :param logger: logging name or object to modify, defaults to root logger
    :param level: logging level to set at (10=Debug, 20=Info, 30=Warn, 40=Error)
    """
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.setLevel(level)
    for handler in logger.handlers:
        handler.level = level


def get_registered_loggers(hide_children=False, hide_reusables=False):
    """
    Find the names of all loggers currently registered

    :param hide_children: only return top level logger names
    :param hide_reusables: hide the reusables loggers
    :return: list of logger names
    """

    return [logger for logger in logging.Logger.manager.loggerDict.keys()
            if not (hide_reusables and "reusables" in logger)
            and not (hide_children and "." in logger)]

