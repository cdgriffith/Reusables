#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
import datetime
import time
import re

from .namespace import Namespace

__all__ = ['dt_exps', 'DateTime', 'datetime_regex', 'now']

dt_exps = {"datetime": {
        "format": {
            "%I": re.compile(r"\{(?:12)?\-?hours?\}"),
            "%H": re.compile(r"\{24\-?hours?\}"),
            "%S": re.compile(r"\{seco?n?d?s?\}"),
            "%M": re.compile(r"\{minu?t?e?s?\}"),
            "%f": re.compile(r"\{micro\-?(?:second)?s?\}"),
            "%Z": re.compile(r"\{(?:(tz|time\-?zone))?\}"),
            "%y": re.compile(r"\{years?\}"),
            "%Y": re.compile(r"\{years?\-?(?:(full|name|full\-?name))?s?\}"),
            "%m": re.compile(r"\{months?\}"),
            "%b": re.compile(r"\{months?\-?name\}"),
            "%B": re.compile(r"\{months?\-?(?:(full|full\-?name))?s?\}"),
            "%d": re.compile(r"\{days?\}"),
            "%w": re.compile(r"\{week\-?days?\}"),
            "%j": re.compile(r"\{year\-?days?\}"),
            "%a": re.compile(r"\{(?:week)?\-?days?\-?name\}"),
            "%A": re.compile(r"\{(?:week)?\-?days?\-?fullname\}"),
            "%U": re.compile(r"\{weeks?\}"),
            "%W": re.compile(r"\{mon(?:day)?\-?weeks?\}"),
            "%x": re.compile(r"\{date\}"),
            "%X": re.compile(r"\{time\}"),
            "%c": re.compile(r"\{date\-?time\}"),
            "%z": re.compile(r"\{(?:utc)?\-?offset\}"),
            "%p": re.compile(r"\{periods?\}"),
            "%Y-%m-%dT%H:%M:%S": re.compile(r"\{iso-?(?:format)?\}")
        },
        "date": re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]?"
                           r"\n[\d]{2})"),
        "time": re.compile(r"([\d]{2}:[\d]{2}(?:\.[\d]{6})?)"),
        "datetime": re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]"
                               r"?[\d]{2}T[\d]{2}:[\d]{2}(?:\.[\d]{6})?)")
    }
}

datetime_regex = Namespace(**dt_exps)


class DateTime(datetime.datetime):
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
                                                 datetime.datetime.tzinfo):
            raise TypeError("tzinfo argument must be None or a tzinfo subclass")
        converter = time.localtime if tzinfo is None else time.gmtime
        t = time.time()
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

    def __repr__(self):
        tz = ", tzinfo={}".format(self.tzinfo) if self.tzinfo else ""
        return ("DateTime(year={0.year}, month={0.month}, day={0.day}, "
                "hour={0.hour}, minute={0.minute}, second={0.second}, "
                "microsecond={0.microsecond}{1})".format(self, tz))

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

    @staticmethod
    def from_datetime(dt):
        return DateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                        dt.second, dt.microsecond, dt.tzinfo)

    # Overwrite parent class's creations
    @classmethod
    def now(cls, tz=None):
        return cls.from_datetime(super(DateTime, cls).now(tz))

    @classmethod
    def utcnow(cls):
        return cls.from_datetime(super(DateTime, cls).utcnow())

    @classmethod
    def combine(cls, date, time):
        """Construct a datetime from a given date and a given time."""
        if not isinstance(date, datetime.date):
            raise TypeError("date argument must be a date instance")
        if not isinstance(time, datetime.time):
            raise TypeError("time argument must be a time instance")
        return cls(date.year, date.month, date.day,
                   time.hour, time.minute, time.second, time.microsecond,
                   time.tzinfo)

    @classmethod
    def _fromtimestamp(cls, t, utc, tz):
        """Construct a datetime from a POSIX timestamp (like time.time()).

        A timezone info object may be passed in as well.
        """
        return cls.from_datetime(super(DateTime,
                                       cls)._fromtimestamp(t, utc, tz))

    @classmethod
    def fromtimestamp(cls, t, tz=None):
        """Construct a datetime from a POSIX timestamp (like time.time()).

        A timezone info object may be passed in as well.
        """
        return cls.from_datetime(super(DateTime, cls).fromtimestamp(t, tz))

    @classmethod
    def utcfromtimestamp(cls, t):
        """Construct a naive UTC datetime from a POSIX timestamp."""
        return cls.from_datetime(super(DateTime, cls).utcfromtimestamp(t))

    @classmethod
    def strptime(cls, date_string, format):
        """
        string, format -> new datetime parsed from a string
        (like time.strptime()).
        """
        return cls.from_datetime(super(DateTime,
                                       cls).strptime(date_string, format))


def now(utc=False, tz=None):
    """
    Get a current DateTime object. By default is local.

    .. code:: python

        reusables.now()
        # DateTime(2016, 12, 8, 22, 5, 2, 517000)

        reusables.now().format("It's {24-hour}:{min}")
        # "It's 22:05"

    :param utc: bool, default False, UTC time not local
    :param tz: TimeZone as specified by the datetime module
    :return: reusables.DateTime
    """
    return DateTime.utcnow() if utc else DateTime.now(tz=tz)
