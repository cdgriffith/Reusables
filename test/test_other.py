#!/usr/bin/env python
# -*- coding: utf-8 -*-
import reusables

from .common_test_data import BaseTestClass


class ReuseTestException(Exception):
    pass


# class Foo(metaclass=reusables.Singleton):
#     def __init__(self, thing):
#         self.thing = thing
#
#     def __call__(self):
#         return self.thing


class TestOther(BaseTestClass):
    def test_exception_ignored(self):
        with reusables.ignored(ReuseTestException):
            raise ReuseTestException()

    def test_defaultlist_init(self):
        reusables.defaultlist(factory=int)

    def test_defaultlist_none(self):
        test = reusables.defaultlist()
        assert test[2] is None

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

    # def test_singleton(self):
    #     """Singleton design pattern test class."""
    #     foo = Foo("BAR")
    #     self.assertIs(foo, Foo("BAZ"))
    #     self.assertEqual(foo.thing, "BAR")
    #     self.assertEqual(Foo("BAZ"), "BAR")
