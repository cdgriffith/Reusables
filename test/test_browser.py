#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import time
import shutil
import tarfile
import tempfile
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))


class TestReuse(unittest.TestCase):

    def test_current_time(self):
        fox = reusables.FirefoxCookies(db=os.path.join(test_root, "firefox_cookies.sqlite"))
        t1 = fox._current_time(length=20)
        t2 = fox._current_time(length=5)
        assert len(t1) == 20
        assert len(t2) == 5
        t3 = fox._current_time(length=10)
        assert time.time() - float(t3) <= 3

    def test_exp_time(self):
        fox = reusables.FirefoxCookies(
            db=os.path.join(test_root, "firefox_cookies.sqlite"))
        t1 = fox._expire_time(length=20)
        t2 = fox._expire_time(length=5)
        assert len(t1) == 20
        assert len(t2) == 5
        t3 = fox._expire_time(length=10, days=10)
        assert (time.time() + 864000) - float(t3) <= 3
