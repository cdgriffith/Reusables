#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import reusables


class TestReusables(unittest.TestCase):

    def test_join_path_clean(self):
        resp = reusables.join_paths('/test/', 'clean/', 'path')
        assert resp == '/test/clean/path/', resp

    def test_join_path_dirty(self):
        resp = reusables.join_paths('/test/', '/dirty/', ' path.file ')
        assert resp == '/test/dirty/path.file', resp

    def test_join_path_clean_strict(self):
        resp = reusables.join_paths('/test/', 'clean/', 'path/', strict=True)
        assert resp == '/test/clean/path/', resp

    def test_join_path_dirty_strict(self):
        resp = reusables.join_paths('/test/', '/dirty/',
                                    ' path.file ', strict=True)
        assert resp == '/dirty/ path.file ', resp

    def test_get_config_dict(self):
        resp = reusables.config_dict('test_config.cfg')
        assert resp == {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}, resp

    def test_get_config_dict_auto(self):
        resp = reusables.config_dict(auto_find=True)
        assert resp == {'Section 1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}, resp

    def test_check_bad_filename(self):
        resp = reusables.check_filename("safeFile?.text")
        assert not resp

    def test_check_good_filename(self):
        resp = reusables.check_filename("safeFile.text")
        assert resp

    def test_safe_bad_filename(self):
        resp = reusables.safe_filename("!?!ThatsNotaFileName.\0ThatsASpaceShip^&*")
        assert not [x for x in ("!", "?", "\0", "^", "&", "*") if x in resp], resp
        assert reusables.check_filename(resp)

    def test_safe_good_filename(self):
        infilename = "SafeFile.txt"
        resp = reusables.safe_filename(infilename)
        assert resp == infilename, resp

    def test_safe_bad_path(self):
        path = "/var/lib\\/test/p?!ath/fi\0lename.txt"
        expected = "/var/lib_/test/p__ath/fi_lename.txt"
        resp = reusables.safe_path(path)
        assert not [x for x in ("!", "?", "\0", "^", "&", "*") if x in resp], resp
        assert resp == expected, resp

    def test_safe_good_path(self):
        path = "/var/lib/test/path/filename.txt"
        resp = reusables.safe_path(path)
        assert resp == path, resp
