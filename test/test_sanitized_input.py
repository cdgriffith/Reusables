#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import reusables
import unittest.mock as mock

from .common_test_data import *

def input(message, index=0):
    return ["0", "1", "a"][max(min)]

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
