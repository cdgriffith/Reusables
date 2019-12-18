#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import reusables

from .common_test_data import *


class TestException(Exception):
    pass


class TestOther(BaseTestClass):

    def test_exception_ignored(self):
        with reusables.ignored(TestException):
            raise TestException()
