import os
import sqlite3
import datetime
import time
import sys

_db_structure = {"chrome": [(52,
                            [("meta",), ("cookies",)],
                            ['creation_utc', 'host_key', 'name', 'value',
                             'path', 'expires_utc', 'secure', 'httponly',
                             'last_access_utc', 'has_expires', 'persistent',
                             'priority', 'encrypted_value', 'firstpartyonly'])],
                 "firefox": [(47, [("moz_cookies",)],
                             ['id', 'baseDomain', 'originAttributes', 'name',
                              'value', 'host', 'path', 'expiry', 'lastAccessed',
                              'creationTime', 'isSecure', 'isHttpOnly', 'appId',
                              'inBrowserElement'])]
                 }

_chrome_insert = ("INSERT INTO cookies (creation_utc, host_key, name, value, "
                  "path, expires_utc, secure, httponly, last_access_utc, "
                  "has_expires, persistent, priority, encrypted_value,"
                  " firstpartyonly) VALUES (?, ?, ?, ?, ?, ?, ?, ?, "
                  "?, ?, ?, ?, ?, ?)")

_firefox_insert = ("INSERT INTO moz_cookies (baseDomain, originAttributes,"
                   " name, value, host, path, expiry, lastAccessed, "
                   "creationTime, isSecure, isHttpOnly, appId, inBrowserElement"
                   ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")


def find_firefox_cookies():
    paths = {
        "win32": "~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\",
        "darwin": "",
        "linux": "~/.mozilla/firefox/"
    }

    base = os.path.expanduser(paths[sys.platform])

    default = [x for x in os.listdir(base) if x.endswith(".default")]
    if not default:
        raise OSError("No default profile in {}".format(base))

    cookies = os.path.join(base, default[0], "cookies.sqlite")
    if not os.path.exists(cookies):
        raise OSError("Cookie does not exist at {}".format(cookies))
    return cookies


def find_chrome_cookies():
    paths = {
        "win32": "~\\AppData\\Local\\Google\\Chrome"
                 "\\User Data\\Default\\Cookies",
        "darwin": "",
        "linux": "~/.config/google-chrome/Default/Cookies"
    }

    cookies = os.path.expanduser(paths[sys.platform])

    if not os.path.exists(cookies):
        raise OSError("Cookie does not exist at {}".format(cookies))
    return cookies


def _get_structure(name, version):
    if version == "current":
        structure = sorted(_db_structure[name],
                           key=lambda x: x[0], reverse=True)[0]
    else:
        try:
            structure = [x for x in _db_structure["firefox"]
                         if x[0] == int(version)][0]
        except (ValueError, IndexError):
            raise AssertionError("Invalid version")
    return structure


def _correct_tables_and_rows(cur, structure, table_name):
    grab_ts = cur.execute("SELECT name FROM sqlite_master "
                          "WHERE type = 'table'")
    tables = grab_ts.fetchall()
    grab_rows = cur.execute("SELECT * FROM ? LIMIT 1", (table_name,))
    cols = [description[0] for description in grab_rows.description]

    assert tables == structure[1], "Got {} not {}".format(tables, structure[1])
    assert cols == structure[2], "Got {} not {}".format(cols, structure[2])


def verify_firefox_db_schema(db, version="current"):
    structure = _get_structure("firefox", version)
    conn = sqlite3.Connection(db)
    cur = conn.cursor()
    try:
        _correct_tables_and_rows(cur, structure, "moz_cookies")
    except AssertionError as err:
        print(str(err))
        return False
    finally:
        conn.close()

    return True


def verify_chrome_db_schema(db, version="current"):
    structure = _get_structure("chrome", version)
    conn = sqlite3.Connection(db)
    cur = conn.cursor()
    try:
        _correct_tables_and_rows(cur, structure, "cookies")
    except AssertionError as err:
        print(str(err))
        return False
    finally:
        conn.close()

    return True


def add_chrome_cookie(db, host, name, value, path="/", expires_at=None,
                      secure=0, http_only=0, has_expires=1, persistent=1,
                      priority=1, encrypted_value="", firstpartyonly=0,
                      ):
    conn = sqlite3.Connection(db)
    cur = conn.cursor()

    c_from_epoc = (datetime.datetime.now() - datetime.datetime(1601, 1, 1))
    creation_utc = str(c_from_epoc.total_seconds()).replace(".", "")
    last_access_utc = creation_utc

    if expires_at:
        assert isinstance(expires_at, datetime.timedelta)
        e_from_epoc = (datetime.datetime.now() - datetime.datetime(1601, 1, 1)
                       + expires_at)
        expires_utc = str(e_from_epoc.total_seconds()).replace(".", "")
    else:
        e_from_epoc = (datetime.datetime.now() - datetime.datetime(1601, 1, 1)
                       + datetime.timedelta(days=365))
        expires_utc = str(e_from_epoc.total_seconds()).replace(".", "")

    try:
        cur.execute(_chrome_insert, (creation_utc, host, name, value, path,
                                     expires_utc, secure, http_only,
                                     last_access_utc, has_expires, persistent,
                                     priority, encrypted_value, firstpartyonly))
    except Exception as err:
        raise err
    else:
        conn.commit()
    finally:
        conn.close()


def add_firefox_cookie(db, host, name, value, path="/", expires_at=None,
                       secure=0, http_only=0, origin_attributes="", app_id=0,
                       in_browser_element=0, base_domain=None):

    conn = sqlite3.Connection(db)
    cur = conn.cursor()

    if not base_domain:
        base_domain = ".".join(host.split(".")
                               [-2 if not host.endswith(".co.uk") else -3:])

    creation = last_access = str(time.time()).replace(".", "")[:16].zfill(16)

    if expires_at:
        assert isinstance(expires_at, datetime.timedelta)
        e_from_epoc = (datetime.datetime.now() + expires_at)
    else:
        e_from_epoc = (datetime.datetime.now() + datetime.timedelta(days=365))
    expiry = str(int(time.mktime(e_from_epoc.timetuple())))

    try:
        cur.execute(_firefox_insert, (base_domain, origin_attributes, name,
                                      value, host, path, expiry, last_access,
                                      creation, secure, http_only,
                                      app_id, in_browser_element))
    except Exception as err:
        raise err
    else:
        conn.commit()
    finally:
        conn.close()

