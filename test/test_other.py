#!/usr/bin/env python
# -*- coding: utf-8 -*-
import reusables

from .common_test_data import *


class TestException(Exception):
    pass


class TestOther(BaseTestClass):
    def test_exception_ignored(self):
        with reusables.ignored(TestException):
            raise TestException()

    def test_defaultlist_init(self):
        test = reusables.defaultlist(factory=int)

    def test_defaultlist_length(self):
        test = reusables.defaultlist(factory=int)
        self.assertEqual(len(test), 0)
        x = test[5]
        self.assertEqual(x, 0)
        self.assertIsInstance(x, int)
        self.assertEqual(len(test), 6)

    def test_defaultlist_list_factory(self):
        test = reusables.defaultlist(factory=list)
        test[2].append(10)
        self.assertEqual(test, [[], [], [10]])
