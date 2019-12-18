#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2019 - Chris Griffith - MIT License
from __future__ import absolute_import
import datetime
import re

from reusables.namespace import Namespace

__all__ = ['dt_exps', 'datetime_regex', 'now', 'datetime_format',
           'datetime_from_iso', 'dtf', 'dtiso']

dt_exps = {"datetime": {
        "format": {
            "%I": re.compile(r"{(?:12)?-?hours?}"),
            "%H": re.compile(r"{24-?hours?}"),
            "%S": re.compile(r"{seco?n?d?s?}"),
            "%M": re.compile(r"{minu?t?e?s?}"),
            "%f": re.compile(r"{micro-?(?:second)?s?}"),
            "%Z": re.compile(r"{(?:(tz|time-?zone))?}"),
            "%y": re.compile(r"{years?}"),
            "%Y": re.compile(r"{years?-?(?:(full|name|full-?name))?s?}"),
            "%m": re.compile(r"{months?}"),
            "%b": re.compile(r"{months?-?name}"),
            "%B": re.compile(r"{months?-?(?:(full|full-?name))?s?}"),
            "%d": re.compile(r"{days?}"),
            "%w": re.compile(r"{week-?days?}"),
            "%j": re.compile(r"{year-?days?}"),
            "%a": re.compile(r"{(?:week)?-?days?-?name}"),
            "%A": re.compile(r"{(?:week)?-?days?-?fullname}"),
            "%U": re.compile(r"{weeks?}"),
            "%W": re.compile(r"{mon(?:day)?-?weeks?}"),
            "%x": re.compile(r"{date}"),
            "%X": re.compile(r"{time}"),
            "%c": re.compile(r"{date-?time}"),
            "%z": re.compile(r"{(?:utc)?-?offset}"),
            "%p": re.compile(r"{periods?}"),
            "%Y-%m-%dT%H:%M:%S": re.compile(r"{iso-?(?:format)?}")
        },
        "date": re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]?"
                           r"\n[\d]{2})"),
        "time": re.compile(r"([\d]{2}:[\d]{2}(?:\.[\d]{6})?)"),
        "datetime": re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}"
                               r"[\- _\\/]?[\d]{2}T[\d]{2}:[\d]{2}"
                               r"(?:\.[\d]{6})?)")
    }
}

datetime_regex = Namespace(**dt_exps)


def datetime_format(desired_format, datetime_instance=None,  *args, **kwargs):
    """
    Replaces format style phrases (listed in the dt_exps dictionary)
    with this datetime instance's information.

    .. code :: python

        reusables.datetime_format("Hey, it's {month-full} already!")
        "Hey, it's March already!"

    :param desired_format: string to add datetime details too
    :param datetime_instance: datetime.datetime instance, defaults to 'now'
    :param args: additional args to pass to str.format
    :param kwargs: additional kwargs to pass to str format
    :return: formatted string
    """
    for strf, exp in datetime_regex.datetime.format.items():
        desired_format = exp.sub(strf, desired_format)
    if not datetime_instance:
        datetime_instance = now()
    return datetime_instance.strftime(desired_format.format(*args, **kwargs))


def datetime_from_iso(iso_string):
    """
    Create a DateTime object from a ISO string

    .. code :: python

        reusables.datetime_from_iso('2019-03-10T12:56:55.031863')
        datetime.datetime(2019, 3, 10, 12, 56, 55, 31863)

    :param iso_string: string of an ISO datetime
    :return: DateTime object
    """
    try:
        assert datetime_regex.datetime.datetime.match(iso_string).groups()[0]
    except (ValueError, AssertionError, IndexError, AttributeError):
        raise TypeError("String is not in ISO format")
    try:
        return datetime.datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S")


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
    return datetime.datetime.utcnow() if utc else datetime.datetime.now(tz=tz)

dtf = datetime_format
dtiso = datetime_from_iso
