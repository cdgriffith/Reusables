#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import unittest
import os
import reusables
import datetime

test_root = os.path.abspath(os.path.dirname(__file__))


class TestReuseDatetime(unittest.TestCase):

    def test_datetime_from_iso(self):
        test = datetime.datetime.now()
        testiso = test.isoformat()
        dt = reusables.DateTime.from_iso(testiso)
        assert dt.hour == dt.hour
        assert test == dt
        assert isinstance(dt, reusables.DateTime)

    def test_datetime_from_iso_v2(self):
        test = datetime.datetime.now()
        testiso = test.isoformat()
        testiso = testiso.rsplit(".", 1)[0]
        dt = reusables.DateTime.from_iso(testiso)
        assert dt.hour == test.hour
        assert test.minute == dt.minute
        assert dt.microsecond == 0, dt.microsecond
        assert isinstance(dt, reusables.DateTime)

    def test_datetime_from_bad_iso(self):
        try:
            reusables.DateTime.from_iso("hehe not a real time")
        except TypeError:
            assert True
        else:
            assert False, "How is that a datetime???"

    def test_datetime_iter(self):
        for k, v in reusables.DateTime():
            if k != "timezone":
                assert v is not None, k

    def test_datetime_new(self):
        now = reusables.DateTime()
        today = datetime.datetime.now()
        assert now.day == today.day
        assert now.year == today.year
        assert now.hour == today.hour

    def test_datetime_format(self):
        now = reusables.DateTime()
        assert now.format("{hour}:{minute}:{second}") == now.strftime("%I:%M:%S"), (
        now.strftime("%I:%M:%S"), now.format("{hour}:{minute}:{second}"))
        assert now.format(
            "{hour}:{minute}:{hour}:{24hour}:{24-hour}") == now.strftime(
            "%I:%M:%I:%H:%H"), now.format(
            "{hour}:{minute}:{hour}:{24hour}:{24-hour}")
