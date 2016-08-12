#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2016 - Chris Griffith - MIT License
"""
A hopefully easier to use formatting system for datetime.
"""
import datetime as _datetime
import time as _time
import re as _re

from .namespace import Namespace

dt_exps = {"datetime": {
        "format": {
            "%I": _re.compile(r"\{(?:12)?\-?hours?\}"),
            "%H": _re.compile(r"\{24\-?hours?\}"),
            "%S": _re.compile(r"\{seco?n?d?s?\}"),
            "%M": _re.compile(r"\{minu?t?e?s?\}"),
            "%f": _re.compile(r"\{micro\-?(?:second)?s?\}"),
            "%Z": _re.compile(r"\{(?:(tz|time\-?zone))?\}"),
            "%y": _re.compile(r"\{years?\}"),
            "%Y": _re.compile(r"\{years?\-?(?:(full|name|full\-?name))?s?\}"),
            "%m": _re.compile(r"\{months?\}"),
            "%b": _re.compile(r"\{months?\-?name\}"),
            "%B": _re.compile(r"\{months?\-?(?:(full|full\-?name))?s?\}"),
            "%d": _re.compile(r"\{days?\}"),
            "%w": _re.compile(r"\{week\-?days?\}"),
            "%j": _re.compile(r"\{year\-?days?\}"),
            "%a": _re.compile(r"\{(?:week)?\-?days?\-?name\}"),
            "%A": _re.compile(r"\{(?:week)?\-?days?\-?fullname\}"),
            "%U": _re.compile(r"\{weeks?\}"),
            "%W": _re.compile(r"\{mon(?:day)?\-?weeks?\}"),
            "%x": _re.compile(r"\{date\}"),
            "%X": _re.compile(r"\{time\}"),
            "%c": _re.compile(r"\{date\-?time\}"),
            "%z": _re.compile(r"\{(?:utc)?\-?offset\}"),
            "%p": _re.compile(r"\{periods?\}"),
            "%Y-%m-%dT%H:%M:%S": _re.compile(r"\{iso-?(?:format)?\}")
        },
        "date": _re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]?"
                           r"\n[\d]{2})"),
        "time": _re.compile(r"([\d]{2}:[\d]{2}(?:\.[\d]{6})?)"),
        "datetime": _re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]"
                               r"?[\d]{2}T[\d]{2}:[\d]{2}(?:\.[\d]{6})?)")
    }
}

datetime_regex = Namespace(**dt_exps)


class DateTime(_datetime.datetime):
    """
    Custom DateTime object compatible with datetime.datetime that adds easy
    string formatting and ISO string parsing.
    """

    def __new__(cls, year=None, month=None, day=None, hour=0, minute=0,
                second=0, microsecond=0, tzinfo=None):
        #  Taken from datetime.datetime.now()
        if year is not None:
            return super(DateTime, cls).__new__(cls, year, month, day, hour,
                                                minute, second, microsecond,
                                                tzinfo)
        if tzinfo is not None and not isinstance(tzinfo,
                                                 _datetime.datetime.tzinfo):
            raise TypeError("tzinfo argument must be None or a tzinfo subclass")
        converter = _time.localtime if tzinfo is None else _time.gmtime
        t = _time.time()
        t, frac = divmod(t, 1.0)
        us = int(frac * 1e6)
        tz = None
        if us == 1000000:
            t += 1
            us = 0
        y, m, d, hh, mm, ss, weekday, jday, dst = converter(t)
        ss = min(ss, 59)
        return super(DateTime, cls).__new__(cls, y, m, d, hh, mm, ss, us, tz)

    def __init__(self, *args):
        self.__dict__ = dict(
            year=self.year, month=self.month, day=self.day, hour=self.hour,
            minute=self.minute, second=self.second,
            microsecond=self.microsecond, timezone=self.tzinfo)

    def format(self, desired_format, *args, **kwargs):
        """
        Replaces format style phrases (listed in the dt_exps dictionary)
        with this datetime instance's information.

        :param desired_format: string to add datetime details too
        :param args: additional args to pass to str.format
        :param kwargs: additional kwargs to pass to str format
        :return: formatted string
        """
        for strf, exp in datetime_regex.datetime.format.items():
            desired_format = exp.sub(strf, desired_format)
        return self.strftime(desired_format.format(*args, **kwargs))

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield (k, v)

    @classmethod
    def from_iso(cls, iso_datetime):
        """
        Create a DateTime object from a ISO string

        :param iso_datetime: string of an ISO datetime
        :return: DateTime object
        """
        try:
            assert datetime_regex.datetime.datetime.match(
                iso_datetime).groups()[0]
        except (ValueError, AssertionError, IndexError, AttributeError):
            raise TypeError("String is not in ISO format")
        try:
            return cls.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            return cls.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S")

    # TODO add a 'from datetime'