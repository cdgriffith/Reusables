#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2016 - Chris Griffith - MIT License
"""
Classes for managing Firefox and Chrome Cookies
"""

import os as _os
import sqlite3 as _sqlite3
import datetime as _dt
import sys as _sys

from .log import get_logger

logger = get_logger(__name__)


def _to_secs(td):
    """Compatibility for 2.6 and 3.2 for timedelta.total_seconds()"""
    if (_sys.version_info[0:2] < (2, 7) or
       (2, 7) < _sys.version_info[0:2] < (3, 3)):
        return ((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 **
                6) / 10 ** 6)
    else:
        return td.total_seconds()


def _get_platform():
    if "linux" in _sys.platform:
        return "linux"
    elif "darwin" in _sys.platform:
        return "mac"
    elif _sys.platform in ("win32", "cygwin"):
        return "windows"
    else:
        raise BrowserException("Unsupported Platform for"
                               " automation profile gathering")


class BrowserException(Exception):
    """Generic parent exception for errors in this module"""


class InvalidSchema(BrowserException):
    """The provided DB did not have a valid scheme"""


class CookieManager(object):
    """
    Parent class for all cookies managers for better cross browser
    compatibilities and portability.
    """
    _valid_structure = {"tables": [],
                        "columns": []}
    _db_paths = {
        "window": "",
        "mac": "",
        "linux": ""}
    _insert = ""
    db = ""
    table_name = ""
    supported_versions = ()

    def __init__(self, db=None):
        self.db = db if db else self.find_db()
        self.verify_schema()

    def _correct_tables_and_titles(self, cur):
        """Performs table and column name lookup and makes sure they match the
        defined valid schema.
        :param cur: SQLite cursor
        :type cur: sqlite3.Connection.cursor"""

        grab_ts = cur.execute("SELECT name FROM sqlite_master "
                              "WHERE type = 'table'")
        tables = grab_ts.fetchall()
        grab_row = cur.execute("SELECT * FROM {0} LIMIT 1".format(
            self.table_name))
        cols = [description[0] for description in grab_row.description]

        if tables != self._valid_structure["tables"]:
            raise InvalidSchema("Tables expected {0} - Got {1}".format(
                self._valid_structure["tables"], tables))
        if cols != self._valid_structure["columns"]:
            raise InvalidSchema("Columns expected {0} - Got {1}".format(
                self._valid_structure["columns"], cols))

    def verify_schema(self):
        """Match the selected DB to the class's valid schema to verify
        compatibility."""
        conn = _sqlite3.Connection(self.db)
        cur = conn.cursor()
        try:
            self._correct_tables_and_titles(cur)
        finally:
            conn.close()

    def find_db(self):
        """Look at the default profile path based on system platform to
        find the browser's cookie database."""
        cookies_path = _os.path.expanduser(self._db_paths[_get_platform()])

        cookies_path = self._find_db_extra(cookies_path)

        if not _os.path.exists(cookies_path):
            raise BrowserException("Cookie does not exist at "
                                   "{0}".format(cookies_path))
        return cookies_path

    @staticmethod
    def _find_db_extra(expanded_path):
        """Some browser's profiles require path manipulation"""
        return expanded_path

    @staticmethod
    def _current_time(epoch=_dt.datetime(1970, 1, 1), length=16):
        """Returns a string of the current time based on epoc date at a set
         length of integers."""
        delta_from_epic = (_dt.datetime.utcnow() - epoch)
        return int(str(_to_secs(delta_from_epic)
                       ).replace(".", "")[:length].ljust(length, "0"))

    @staticmethod
    def _expire_time(epoch=_dt.datetime(1970, 1, 1), length=10, days=365,
                     hours=0):
        """Returns a string of time based on epoch date at a set
         length of integers with an additional timedetla of specified days
        and/or hours."""
        delta_from_epic = (_dt.datetime.utcnow() - epoch +
                           _dt.timedelta(days=days, hours=hours))
        return int(str(_to_secs(delta_from_epic)
                       ).replace(".", "")[:length].ljust(length, "0"))

    def _insert_command(self, cursor, host, name, value, path,
                        expires_at, secure, http_only, **extra):
        """Child class must override"""
        raise NotImplementedError()

    def _delete_command(self, cursor, host, name):
        """Child class must override"""
        raise NotImplementedError()

    def add_cookie(self, host, name, value, path="/", expires_at=None, secure=0,
                   http_only=0, **extra):
        """Abstracted function to add a cookie to the database."""
        conn = _sqlite3.Connection(self.db)
        cur = conn.cursor()
        try:
            self._insert_command(cur, host, name, value, path, expires_at,
                                 secure, http_only, **extra)
        except Exception as err:
            raise BrowserException(str(err))
        else:
            conn.commit()
        finally:
            conn.close()

    def delete_cookie(self, host, name):
        """Abstracted function to remove a cookie from the database."""
        conn = _sqlite3.Connection(self.db)
        cur = conn.cursor()
        try:
            self._delete_command(cur, host, name)
        except Exception as err:
            raise BrowserException(str(err))
        else:
            conn.commit()
        finally:
            conn.close()

    def update_cookie(self, host, name, value, path="/", expires_at=None,
                      secure=0, http_only=0, ignore_missing=True, **extra):
        """Delete and re-add a cookie with different value."""
        conn = _sqlite3.Connection(self.db)
        cur = conn.cursor()

        try:
            self._delete_command(cur, host, name)
        except Exception as err:
            if not ignore_missing:
                raise BrowserException(str(err))

        try:
            self._insert_command(cur, host, name, value, path, expires_at,
                                 secure, http_only, **extra)
        except Exception as err:
            raise BrowserException(str(err))
        else:
            conn.commit()
        finally:
            conn.close()


class FirefoxCookiesV1(CookieManager):
    """First iteration of Firefox Cookie manager"""
    _valid_structure = {"tables": [("moz_cookies",)],
                        "columns": ['id', 'baseDomain', 'originAttributes',
                                    'name', 'value', 'host', 'path', 'expiry',
                                    'lastAccessed', 'creationTime', 'isSecure',
                                    'isHttpOnly', 'appId', 'inBrowserElement']}

    _insert = ("INSERT INTO moz_cookies (baseDomain, originAttributes,"
               " name, value, host, path, expiry, lastAccessed, "
               "creationTime, isSecure, isHttpOnly, appId, inBrowserElement"
               ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

    _db_paths = {
        "windows": "~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\",
        "mac": "~/Library/Application Support/Firefox/Profiles/",
        "linux": "~/.mozilla/firefox/"}
    table_name = "moz_cookies"
    supported_versions = (47, 48)

    @staticmethod
    def _find_db_extra(expanded_path):
        """Firefox profiles path has a folder that ends with .default that
        must be found."""
        default = [x for x in _os.listdir(expanded_path)
                   if x.endswith(".default")]
        if not default:
            raise BrowserException("No default profile in "
                                   "{0}".format(expanded_path))
        return _os.path.join(expanded_path, default[0], "cookies.sqlite")

    def _insert_command(self, cursor, host, name, value, path,
                        expires_at, secure, http_only, **extra):
        """Firefox specific SQL insert command with required times"""
        now = self._current_time(length=16)
        exp = self._expire_time(length=10)
        base_domain = extra.get("base_domain", ".".join(host.split(".")
                                [-2 if not host.endswith(".co.uk") else -3:]))

        cursor.execute(self._insert, (base_domain,
                                      extra.get('origin_attributes', ""),
                                      name, value, host, path, exp, now, now,
                                      secure, http_only,
                                      extra.get('app_id', 0),
                                      extra.get('in_browser_element', 0)))

    def _delete_command(self, cursor, host, name):
        """Firefox specific SQL delete command"""
        cursor.execute("DELETE FROM moz_cookies WHERE host=? AND name=?",
                       (host, name))


class ChromeCookiesV1(CookieManager):
    """First iteration of Chrome Cookie manager"""
    _valid_structure = {"tables": [("meta",), ("cookies",)],
                        "columns": ['creation_utc', 'host_key', 'name', 'value',
                                    'path', 'expires_utc', 'secure', 'httponly',
                                    'last_access_utc', 'has_expires',
                                    'persistent', 'priority', 'encrypted_value',
                                    'firstpartyonly']}
    _db_paths = {
        "windows": "~\\AppData\\Local\\Google\\Chrome"
                 "\\User Data\\Default\\Cookies",
        "mac": "~/Library/Application Support/Google/Chrome/Default/Cookies",
        "linux": "~/.config/google-chrome/Default/Cookies"}
    _insert = ("INSERT INTO cookies (creation_utc, host_key, name, value, "
               "path, expires_utc, secure, httponly, last_access_utc, "
               "has_expires, persistent, priority, encrypted_value,"
               " firstpartyonly) VALUES (?, ?, ?, ?, ?, ?, ?, ?, "
               "?, ?, ?, ?, ?, ?)")
    table_name = "cookies"
    supported_versions = (52,)

    def _insert_command(self, cursor, host, name, value, path,
                        expires_at, secure, http_only, **extra):
        """Chrome specific SQL insert command with required times"""
        now = self._current_time(epoch=_dt.datetime(1601, 1, 1), length=17)
        exp = self._expire_time(epoch=_dt.datetime(1601, 1, 1), length=17)

        cursor.execute(self._insert, (now, host, name, value, path, exp, secure,
                                      http_only, now,
                                      extra.get('has_expires', 1),
                                      extra.get('persistent', 1),
                                      extra.get('priority', 1),
                                      extra.get('encrypted_value', ""),
                                      extra.get('first_party_only', 0)))

    def _delete_command(self, cursor, host, name):
        """Chrome specific SQL delete command"""
        cursor.execute("DELETE FROM cookies WHERE host_key=? AND name=?",
                       (host, name))


class FirefoxCookies(FirefoxCookiesV1):
    """Current version of Firefox cookie management"""


class ChromeCookies(ChromeCookiesV1):
    """Current version of Chrome cookie management"""
