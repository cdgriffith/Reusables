#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import datetime
import sys


class CookieManager(object):
    _valid_structure = {"tables": [],
                        "columns": []}
    _db_paths = {
        "win32": "",
        "darwin": "",
        "linux": ""}
    _insert = ""
    db = ""
    table_name = ""

    def __init__(self, db=None):
        self.db = db if db else self.find_db()
        self.verify_schema()

    def _correct_tables_and_rows(self, cur):
        grab_ts = cur.execute("SELECT name FROM sqlite_master "
                              "WHERE type = 'table'")
        tables = grab_ts.fetchall()
        grab_row = cur.execute("SELECT * FROM {} LIMIT 1".format(
            self.table_name))
        cols = [description[0] for description in grab_row.description]

        if tables != self._valid_structure["tables"]:
            raise AssertionError("Expected {} - Got {}".format(
                self._valid_structure["tables"], tables))
        if cols != self._valid_structure["columns"]:
            raise AssertionError("Expected {} - Got {}".format(
                self._valid_structure["columns"], cols))

    def verify_schema(self):
        conn = sqlite3.Connection(self.db)
        cur = conn.cursor()
        try:
            self._correct_tables_and_rows(cur)
        except AssertionError as err:
            print(str(err))
            return False
        finally:
            conn.close()
        return True

    def find_db(self):
        cookies_path = os.path.expanduser(self._db_paths[sys.platform])

        cookies_path = self._find_db_extra(cookies_path)

        if not os.path.exists(cookies_path):
            raise OSError("Cookie does not exist at {}".format(cookies_path))
        return cookies_path

    @staticmethod
    def _find_db_extra(expanded_path):
        return expanded_path

    @staticmethod
    def _current_time(epoch=datetime.datetime(1970, 1, 1), length=16):
        delta_from_epic = (datetime.datetime.utcnow() - epoch)
        return str(delta_from_epic.total_seconds()
                   ).replace(".", "")[:length].zfill(length)

    @staticmethod
    def _expire_time(epoch=datetime.datetime(1970, 1, 1), length=10, days=365):
        delta_from_epic = (datetime.datetime.utcnow() - epoch
                           + datetime.timedelta(days=days))
        return str(delta_from_epic.total_seconds()
                   ).replace(".", "")[:length].zfill(length)

    def _insert_command(self, cursor, host, name, value, path,
                        expires_at, secure, http_only, **extra):
        return

    def add_cookie(self, host, name, value, path="/", expires_at=None, secure=0,
                   http_only=0, **extra):
        conn = sqlite3.Connection(self.db)
        cur = conn.cursor()
        try:
            self._insert_command(cur, host, name, value, path, expires_at,
                                 secure, http_only, **extra)
        except Exception as err:
            raise err
        else:
            conn.commit()
        finally:
            conn.close()


class FirefoxCookies(CookieManager):
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
        "win32": "~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\",
        "darwin": "~/Library/Application Support/Firefox/Profiles/",
        "linux": "~/.mozilla/firefox/"}
    table_name = "moz_cookies"

    @staticmethod
    def _find_db_extra(expanded_path):
        default = [x for x in os.listdir(expanded_path)
                   if x.endswith(".default")]
        if not default:
            raise OSError("No default profile in {}".format(expanded_path))
        return os.path.join(expanded_path, default[0], "cookies.sqlite")

    def _insert_command(self, cursor, host, name, value, path,
                        expires_at, secure, http_only, **extra):
        now = self._current_time(length=16)
        print(now)
        exp = self._expire_time(length=10)
        print(exp)
        base_domain = extra.get("base_domain", ".".join(host.split(".")
                                [-2 if not host.endswith(".co.uk") else -3:]))

        cursor.execute(self._insert, (base_domain,
                                      extra.get('origin_attributes', ""),
                                      name, value, host, path, exp, now, now,
                                      secure, http_only,
                                      extra.get('app_id', 0),
                                      extra.get('in_browser_element', 0)))


class ChromeCookies(CookieManager):
    _valid_structure = {"tables": [("meta",), ("cookies",)],
                        "columns": ['creation_utc', 'host_key', 'name', 'value',
                                    'path', 'expires_utc', 'secure', 'httponly',
                                    'last_access_utc', 'has_expires',
                                    'persistent', 'priority', 'encrypted_value',
                                    'firstpartyonly']}
    _db_paths = {
        "win32": "~\\AppData\\Local\\Google\\Chrome"
                 "\\User Data\\Default\\Cookies",
        "darwin": "~/Library/Application Support/Google/Chrome/Default/Cookies",
        "linux": "~/.config/google-chrome/Default/Cookies"}
    _insert = ("INSERT INTO cookies (creation_utc, host_key, name, value, "
               "path, expires_utc, secure, httponly, last_access_utc, "
               "has_expires, persistent, priority, encrypted_value,"
               " firstpartyonly) VALUES (?, ?, ?, ?, ?, ?, ?, ?, "
               "?, ?, ?, ?, ?, ?)")
    table_name = "cookies"

    def _insert_command(self, cursor, host, name, value, path,
                        expires_at, secure, http_only, **extra):
        now = self._current_time(epoch=datetime.datetime(1601, 1, 1), length=17)
        exp = self._expire_time(epoch=datetime.datetime(1601, 1, 1), length=17)

        cursor.execute(self._insert, (now, host, name, value, path, exp, secure,
                                      http_only, now,
                                      extra.get('has_expires', 1),
                                      extra.get('persistent', 1),
                                      extra.get('priority', 1),
                                      extra.get('encrypted_value', ""),
                                      extra.get('first_party_only', 0)))


