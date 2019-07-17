#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import reusables
try:
    import unittest.mock as mock
except ImportError:
    from mock import mock

from .common_test_data import *


class TestException(Exception):
    pass


class IntVar:
    def __init__(self, value):
        if isinstance(value, str):
            self.value = int(value)
        else:
            raise TestException("Exception")


class TestSanitizedInput(BaseTestClass):

    def test_count_exceeded(self):
        kwargs = {"message": "",
                  "cast_as": int,
                  "number_of_retries": 1,
                  "error_message": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('reusables.sanitizers._get_input', return_value="x"):
            self.assertRaises(reusables.RetryCountExceededError,
                              reusables.sanitized_input, **kwargs)

    def test_cast_int(self):
        kwargs = {"message": "",
                  "cast_as": int,
                  "number_of_retries": -1,
                  "error_message": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('reusables.sanitizers._get_input', return_value="32"):
            self.assertEqual(32, reusables.sanitized_input(**kwargs))

    def test_cast_as(self):
        kwargs = {"message": "",
                  "cast_as": IntVar,
                  "number_of_retries": -1,
                  "error_message": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('reusables.sanitizers._get_input', return_value=1):
            self.assertRaises(TestException,
                              reusables.sanitized_input, **kwargs)
        with mock.patch('reusables.sanitizers._get_input', return_value='1'):
            assert isinstance(reusables.sanitized_input(cast_as=IntVar), IntVar), "Success"
            assert not isinstance(reusables.sanitized_input(cast_as=IntVar), int), "Failure"

    def test_cast_successful(self):
        with mock.patch('reusables.sanitizers._get_input', return_value='1'):
            assert isinstance(reusables.sanitized_input(cast_as=int), int), 'Success'
            assert not isinstance(reusables.sanitized_input(cast_as=str), int), 'Failure'
            assert isinstance(reusables.sanitized_input(cast_as=str), str), 'Success'

    def test_valid_input(self):
        kwargs = {"message": "",
                  "cast_as": str,
                  "number_of_retries": -1,
                  "error_message": "",
                  "valid_input": ["1", "2"],
                  "raise_on_invalid": True}
        with mock.patch('reusables.sanitizers._get_input', return_value="3"):
            self.assertRaises(reusables.InvalidInputError,
                              reusables.sanitized_input, **kwargs)

    def test_chain_cast(self):
        kwargs = {"message": "",
                  "cast_as": "int, float",
                  "number_of_retries": -1,
                  "error_message": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('reusables.sanitizers._get_input', return_value="3.2"):
            assert isinstance(reusables.sanitized_input(cast_as=[int, float]), int)
            self.assertRaises(ValueError, reusables.sanitized_input, **kwargs)

