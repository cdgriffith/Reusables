#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import logging
import reusables
import sys

from .common_test_data import *

my_stream_path = os.path.join(test_root, "my_stream.log")
my_fiie_path = os.path.join(test_root, "my_file.log")

if sys.version_info < (2, 7):
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

    logging.NullHandler = NullHandler


class TestReuseLogging(BaseTestClass):

    def setUp(self):
        logging.getLogger(__name__).handlers = []
        if os.path.exists(my_stream_path):
            try:
                os.unlink(my_stream_path)
            except WindowsError:
                pass

    @classmethod
    def tearDownClass(cls):
        log = logging.getLogger(__name__)
        reusables.remove_all_handlers(log)

        if os.path.exists(my_stream_path):
            try:
                os.unlink(my_stream_path)
            except WindowsError:
                pass

    def test_get_stream_logger(self):
        my_stream = open(my_stream_path, "w")
        logger = reusables.get_logger(__name__, stream=my_stream)
        logger.info("Test log")
        logger.error("Example error log")
        my_stream.close()
        reusables.remove_all_handlers(logger)
        with open(my_stream_path) as f:
            lines = f.readlines()
        assert "INFO" in lines[0]
        assert "ERROR" in lines[1]
        assert "Example error log" in lines[1]

    def test_add_file_logger(self):
        logger = reusables.get_logger(__name__)
        reusables.add_file_handler(logger, my_fiie_path)
        logger.info("Test log")
        logger.error("Example error log")
        reusables.remove_all_handlers(logger)
        with open(my_fiie_path) as f:
            lines = f.readlines()
        assert "INFO" in lines[0]
        assert "ERROR" in lines[1]
        assert "Example error log" in lines[1]

    def test_change_log_level(self):
        logger = reusables.get_logger(__name__,
                                      level=logging.WARNING,
                                      stream=None,
                                      file_path=my_stream_path)
        logger.debug("Hello There, sexy")
        reusables.change_logger_levels(__name__, 10)
        logger.debug("This isn't a good idea")
        reusables.remove_file_handlers(logger)
        with open(my_stream_path) as f:
            line = f.readline()
        assert "good idea" in line, line

    def test_get_file_logger(self):
        logger = reusables.get_logger(__name__, stream=None,
                                      file_path=my_stream_path)
        logger.info("Test log")
        logger.error("Example 2nd error log")
        reusables.remove_file_handlers(logger)
        with open(my_stream_path) as f:
            lines = f.readlines()
        assert "INFO" in lines[0]
        assert "ERROR" in lines[1]
        assert "Example 2nd error log" in lines[1]

    def test_add_null(self):
        logger = reusables.get_logger("add_null", stream=None, suppress_warning=True)
        assert isinstance(logger.handlers[0], logging.NullHandler)

    def test_remove_stream_handlers(self):
        logger = reusables.get_logger("sample_stream_logger", file_path=my_stream_path)
        logger.addHandler(logging.NullHandler())
        for _ in range(10):
            logger.addHandler(reusables.get_stream_handler())
        reusables.remove_stream_handlers("sample_stream_logger")
        assert len(logger.handlers) == 2, logger.handlers
        assert isinstance(logger.handlers[0], logging.FileHandler)
        reusables.remove_all_handlers(logger)

    def test_remove_file_handlers(self):
        logger = reusables.get_logger("sample_file_logger", file_path=my_stream_path)
        logger.addHandler(logging.FileHandler("test_file"))
        logger.addHandler(logging.NullHandler())
        reusables.remove_file_handlers("sample_file_logger")
        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        try:
            os.unlink("test_file")
        except Exception:
            pass
        reusables.remove_all_handlers(logger)

    def test_add_rotate_file_handlers(self):
        from logging.handlers import RotatingFileHandler,\
            TimedRotatingFileHandler
        logger = reusables.get_logger("add_file")
        reusables.remove_all_handlers(logger)
        reusables.add_rotating_file_handler("add_file")
        assert isinstance(logger.handlers[0], RotatingFileHandler), logger.handlers
        reusables.remove_all_handlers("add_file")
        reusables.add_timed_rotating_file_handler("add_file")
        assert isinstance(logger.handlers[0], TimedRotatingFileHandler)
        reusables.remove_all_handlers("add_file")

    def test_add_simple_handlers(self):
        logger = reusables.get_logger("test1")
        reusables.remove_all_handlers("test1")
        reusables.add_stream_handler("test1")
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        reusables.remove_all_handlers("test1")


