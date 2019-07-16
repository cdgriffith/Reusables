#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import reusables
import unittest.mock as mock

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
                  "cast_obj": int,
                  "n_retries": 1,
                  "error_msg": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('builtins.input', return_value="x"):
            self.assertRaises(reusables.RetryCountExceededError,
                              reusables.sanitized_input, **kwargs)

    def test_cast_int(self):
        kwargs = {"message": "",
                  "cast_obj": int,
                  "n_retries": -1,
                  "error_msg": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('builtins.input', return_value="32"):
            self.assertEqual(32,
                             reusables.sanitized_input(**kwargs))

    def test_cast_obj(self):
        kwargs = {"message": "",
                  "cast_obj": IntVar,
                  "n_retries": -1,
                  "error_msg": "",
                  "valid_input": [],
                  "raise_on_invalid": False}
        with mock.patch('builtins.input', return_value=1):
            self.assertRaises(TestException,
                              reusables.sanitized_input, **kwargs)
        with mock.patch('builtins.input', return_value='1'):
            assert isinstance(reusables.sanitized_input(cast_obj=IntVar), IntVar), "Success"
            assert not isinstance(reusables.sanitized_input(cast_obj=IntVar), int), "Failure"

    def test_cast_successful(self):
        with mock.patch('builtins.input', return_value='1'):
            assert isinstance(reusables.sanitized_input(cast_obj=int), int), 'Success'
            assert not isinstance(reusables.sanitized_input(cast_obj=str), int), 'Failure'
            assert isinstance(reusables.sanitized_input(cast_obj=str), str), 'Success'

    def test_valid_input(self):
        kwargs = {"message": "",
                  "cast_obj": str,
                  "n_retries": 1,
                  "error_msg": "",
                  "valid_input": ["1", "2"],
                  "raise_on_invalid": True}
        with mock.patch('builtins.input', return_value="3"):
            self.assertRaises(reusables.InvalidInputError,
                              reusables.sanitized_input, **kwargs)
