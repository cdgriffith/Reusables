#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime

import reusables

from .common_test_data import *


class TestDateTime(BaseTestClass):

    def test_datetime_from_iso(self):
        test = datetime.datetime.now()
        testiso = test.isoformat()
        dt = reusables.datetime_from_iso(testiso)
        assert dt.hour == dt.hour
        assert test == dt

    def test_datetime_from_iso_v2(self):
        test = datetime.datetime.now()
        testiso = test.isoformat()
        testiso = testiso.rsplit(".", 1)[0]
        dt = reusables.datetime_from_iso(testiso)
        assert dt.hour == test.hour
        assert test.minute == dt.minute
        assert dt.microsecond == 0, dt.microsecond

    def test_datetime_from_bad_iso(self):
        try:
            reusables.datetime_from_iso("hehe not a real time")
        except TypeError:
            assert True
        else:
            assert False, "How is that a datetime???"

    def test_datetime_new(self):
        now = reusables.now()
        today = datetime.datetime.now()
        assert now.day == today.day
        assert now.year == today.year
        assert now.hour == today.hour

    def test_datetime_format(self):
        assert reusables.dtf("{hour}:{minute}:{second}"
                             ) == datetime.datetime.now().strftime("%I:%M:%S")
        assert reusables.dtf("{hour}:{minute}:{hour}:{24hour}:{24-hour}"
                             ) == datetime.datetime.now().strftime(
            "%I:%M:%I:%H:%H")

    def test_now(self):
        now = reusables.now()
        assert isinstance(now, datetime.datetime)
