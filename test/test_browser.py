#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import time
import shutil
import tarfile
import sqlite3
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))
db = os.path.join(test_root, "firefox_cookies_copy.sqlite")


class TestReuse(unittest.TestCase):

    def setUp(self):
        try:
            os.unlink(db)
        except OSError:
            pass
        shutil.copy(os.path.join(test_root, "firefox_cookies.sqlite"), db)

    @classmethod
    def tearDownClass(cls):
        os.unlink(db)

    def test_current_time(self):
        fox = reusables.FirefoxCookies(db=db)
        t1 = fox._current_time(length=20)
        t2 = fox._current_time(length=5)
        assert len(str(t1)) == 20
        assert len(str(t2)) == 5
        t3 = fox._current_time(length=10)
        assert time.time() - float(t3) <= 3

    def test_exp_time(self):
        fox = reusables.FirefoxCookies(db=db)
        t1 = fox._expire_time(length=20)
        t2 = fox._expire_time(length=5)
        print(t1)
        assert len(str(t1)) == 20
        assert len(str(t2)) == 5
        t3 = fox._expire_time(length=10, days=10)
        assert (time.time() + 864000) - float(t3) <= 3

    def test_firefox_add_cookie(self):
        fox = reusables.FirefoxCookies(db=db)
        fox.add_cookie("www.example.com", "test_name", "test_value")
        conn = sqlite3.Connection(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM {0}".format(fox.table_name))
        res = cur.fetchall()
        assert len(res) == 1
        assert res[0][1] == "example.com"
        assert res[0][3] == "test_name"
        assert res[0][4] == "test_value"
        assert res[0][5] == "www.example.com"
        assert res[0][6] == "/"
        conn.close()

    def test_firefox_update_cookies(self):
        fox = reusables.FirefoxCookies(db=db)
        fox.update_cookie("www.example.com", "test_name1", "test_value1",
                          ignore_missing=True)
        conn = sqlite3.Connection(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM {0}".format(fox.table_name))
        res = cur.fetchall()
        assert len(res) == 1
        assert res[0][3] == "test_name1"
        assert res[0][4] == "test_value1"
        conn.close()

        fox.update_cookie("www.example.com", "test_name1", "test_value2345",
                          ignore_missing=True)

        conn = sqlite3.Connection(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM {0}".format(fox.table_name))
        res = cur.fetchall()
        assert len(res) == 1
        assert res[0][3] == "test_name1"
        assert res[0][4] == "test_value2345"
        conn.close()

    def test_firefox_delete_cookie(self):
        fox = reusables.FirefoxCookies(db=db)
        fox.add_cookie("www.example.com", "test_name", "test_value")
        fox.delete_cookie("www.example.com", "test_name")
        conn = sqlite3.Connection(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM {0}".format(fox.table_name))
        res = cur.fetchall()
        assert len(res) == 0