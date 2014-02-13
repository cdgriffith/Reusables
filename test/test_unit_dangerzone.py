#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
import reuse.dangerzone

@reuse.dangerzone.reuse
def test_func(a,b,c=None):
    return a,b,c


class TestDangerzone(unittest.TestCase):

    def setUp(self):
        test_func(reuse_reset=True)

    def test_reuse_basic(self):
        run1 = test_func(1, 2, 3)
        assert run1 == (1, 2, 3)
        run2 = test_func()
        assert run2 == (1, 2, 3)

    def test_reuse_failure_state(self):
        run1 = test_func(1, 2, 3)
        assert run1 == (1, 2, 3)
        self.assertRaises(TypeError, test_func, *[2,3,4,5,6,7])
        run2 = test_func()
        assert run2 == (1, 2, 3)

    def test_reuse_view_saved(self):
        run1 = test_func(1, 2, 3)
        assert run1 == (1, 2, 3)
        assert test_func(reuse_view_cache=True)['args'] == (1, 2, 3)

    def test_reuse_update_args(self):
        run1 = test_func(1, 2, 3)
        assert run1 == (1, 2, 3)
        assert test_func(reuse_rep_args=[(1, 4)]) == (4, 2, 3)
