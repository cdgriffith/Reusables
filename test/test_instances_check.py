#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import reusables

from .common_test_data import *


class CustomList(list):
    pass


class TestInstancesCheck(BaseTestClass):

    def test_and_instances(self):
        obj = CustomList()
        assert reusables.and_instances(obj, CustomList, list), 'Success'
        assert reusables.and_instances(obj, [CustomList, list]), 'Success'
        assert reusables.and_instances(obj, (CustomList, list)), 'Success'
        assert not reusables.and_instances(obj, (CustomList, tuple)), 'Failure'

    def test_or_instances(self):
        obj = ""
        assert reusables.or_instances(obj, str, int), 'Success'
        assert reusables.or_instances(obj, (str, int)), 'Success'
        assert reusables.or_instances(obj, [str, int]), 'Success'
        assert not reusables.or_instances(obj, [tuple, int]), 'Failure'
