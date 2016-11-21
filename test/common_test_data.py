#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import unittest
import shutil

test_root = os.path.abspath(os.path.dirname(__file__))
data_dr = os.path.join(test_root, "data")

test_structure_tar = os.path.join(data_dr, "test_structure.tar.gz")
test_structure_zip = os.path.join(data_dr, "test_structure.zip")
test_structure_rar = os.path.join(data_dr, "test_structure.rar")
test_structure = os.path.join(test_root, "test_structure")


class BaseTestClass(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(os.path.join(test_root, "test_config.cfg"))
        except OSError:
            pass
        if os.path.exists(test_structure):
            shutil.rmtree(test_structure)
