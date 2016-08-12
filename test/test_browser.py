#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import time
import shutil
import sqlite3
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))
db = os.path.join(test_root, "data", "firefox_cookies_copy.sqlite")


class TestBrowser(reusables.CookieManager):
    def __init__(self):
        pass


class TestReuse(unittest.TestCase):

    def setUp(self):
        try:
            os.unlink(db)
        except OSError:
            pass
        shutil.copy(os.path.join(test_root, "data",
                                 "firefox_cookies.sqlite"), db)

    @classmethod
    def tearDownClass(cls):
        os.unlink(db)

    def test_current_time(self):
        tb = TestBrowser()
        t1 = tb._current_time(length=20)
        t2 = tb._current_time(length=5)
        assert len(str(t1)) == 20
        assert len(str(t2)) == 5
        t3 = tb._current_time(length=10)
        assert time.time() - float(t3) <= 3

    def test_exp_time(self):
        tb = TestBrowser()
        t1 = tb._expire_time(length=20)
        t2 = tb._expire_time(length=5)
        print(t1)
        assert len(str(t1)) == 20
        assert len(str(t2)) == 5
        t3 = tb._expire_time(length=10, days=10)
        assert (time.time() + 864000) - float(t3) <= 3

    def test_overrides(self):
        tb = TestBrowser()
        try:
            tb._insert_command(None, None, None, None, None, None, None, None)
        except NotImplementedError:
            assert True
        else:
            assert False

        try:
            tb._delete_command(None, None, None)
        except NotImplementedError:
            assert True
        else:
            assert False

    def test_firefox_add_cookie(self):
        fox = reusables.FirefoxCookiesV1(db=db)
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
        fox = reusables.FirefoxCookiesV1(db=db)
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
        fox = reusables.FirefoxCookiesV1(db=db)
        fox.add_cookie("www.example.com", "test_name", "test_value")
        fox.delete_cookie("www.example.com", "test_name")
        conn = sqlite3.Connection(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM {0}".format(fox.table_name))
        res = cur.fetchall()
        assert len(res) == 0

    def test_firefox_find_cookies(self):
        try:
            reusables.FirefoxCookies()
        except Exception:
            pass

        _db_paths = {
            "windows": "~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\",
            "mac": "~/Library/Application Support/Firefox/Profiles/",
            "linux": "~/.mozilla/firefox/"}

        path = os.path.expanduser(_db_paths[reusables.browser._get_platform()])
        test_path = os.path.join(path, "reusables_test.default")

        try:
            os.mkdir(test_path)
        except Exception:
            pass

        try:
            reusables.FirefoxCookies()
        except reusables.BrowserException as err:
            assert "Cookie does not exist at" in str(err)
        finally:
            shutil.rmtree(test_path, ignore_errors=True)

