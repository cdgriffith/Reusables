#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import unittest
import os
import logging
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))


class TestReuseLogging(unittest.TestCase):

    my_stream_path = os.path.join(test_root, "my_stream.log")

    def setUp(self):
        logging.getLogger(__name__).handlers = []
        if os.path.exists(self.my_stream_path):
            os.unlink(self.my_stream_path)

    def tearDown(self):
        try:
            os.unlink(self.my_stream_path)
        except Exception:
            pass

    def test_get_stream_logger(self):

        my_stream = open(self.my_stream_path, "w")
        logger = reusables.get_logger(__name__, stream=my_stream)
        logger.info("Test log")
        logger.error("Example error log")
        reusables.remove_all_handlers(logger)
        my_stream.close()
        with open(self.my_stream_path) as f:
            lines = f.readlines()
        assert "INFO" in lines[0]
        assert "ERROR" in lines[1]
        assert "Example error log" in lines[1]

    def test_get_file_logger(self):
        logger = reusables.get_logger(__name__, stream=None, file_path=self.my_stream_path)
        logger.info("Test log")
        logger.error("Example 2nd error log")
        reusables.remove_file_handlers(logger)
        with open(self.my_stream_path) as f:
            lines = f.readlines()
        assert "INFO" in lines[0]
        assert "ERROR" in lines[1]
        assert "Example 2nd error log" in lines[1]

    def test_add_null(self):
        logger = reusables.get_logger(__name__, stream=None, suppress_warning=True)
        assert isinstance(logger.handlers[0], logging.NullHandler)

    def test_remove_stream_handlers(self):
        logger = reusables.get_logger(file_path=self.my_stream_path)
        logger.addHandler(logging.NullHandler())
        reusables.remove_stream_handlers(logger)
        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_remove_file_handlers(self):
        logger = reusables.get_logger(__name__, file_path=self.my_stream_path)
        logger.addHandler(logging.FileHandler("test_file"))
        logger.addHandler(logging.NullHandler())
        reusables.remove_file_handlers(logger)
        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[0], logging.StreamHandler)
