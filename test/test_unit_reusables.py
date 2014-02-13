#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import reuse

test_root = os.path.abspath(os.path.dirname(__file__))

class TestReuse(unittest.TestCase):

    def test_join_path_clean(self):
        resp = reuse.join_paths('/test/', 'clean/', 'path')
        assert resp == '/test/clean/path/', resp

    def test_join_path_dirty(self):
        resp = reuse.join_paths('/test/', '/dirty/', ' path.file ')
        assert resp == '/test/dirty/path.file', resp

    def test_join_path_clean_strict(self):
        resp = reuse.join_paths('/test/', 'clean/', 'path/', strict=True)
        assert resp == '/test/clean/path/', resp

    def test_join_path_dirty_strict(self):
        resp = reuse.join_paths('/test/', '/dirty/',
                                    ' path.file ', strict=True)
        assert resp == '/dirty/ path.file ', resp

    def test_get_config_dict(self):
        resp = reuse.config_dict(os.path.join(test_root, 'test_config.cfg'))
        assert resp == {'Section1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}, resp

    def test_get_config_dict_auto(self):
        resp = reuse.config_dict(auto_find=True)
        assert resp == {'Section1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}, resp

    def test_get_config_dict_no_verify(self):
        resp = reuse.config_dict('bad_loc.cfg', verify=False)
        assert resp == {}, resp

    def test_get_config_namespace(self):
        resp = reuse.config_namespace(os.path.join(test_root,
                                                   'test_config.cfg'))
        assert resp.Section1 == {'key2': 'Value2', 'key 1': 'value 1'}

    def test_check_bad_filename(self):
        resp = reuse.check_filename("safeFile?.text")
        assert not resp

    def test_check_good_filename(self):
        resp = reuse.check_filename("safeFile.text")
        assert resp

    def test_safe_bad_filename(self):
        resp = reuse.safe_filename("!?!ThatsNotaFileName.\0ThatsASpaceShip^&*")
        assert not [x for x in ("!", "?", "\0", "^", "&", "*") if x in resp], resp
        assert reuse.check_filename(resp)

    def test_safe_good_filename(self):
        infilename = "SafeFile.txt"
        resp = reuse.safe_filename(infilename)
        assert resp == infilename, resp

    def test_safe_bad_path(self):
        path = "/var/lib\\/test/p?!ath/fi\0lename.txt"
        expected = "/var/lib_/test/p__ath/fi_lename.txt"
        resp = reuse.safe_path(path)
        assert not [x for x in ("!", "?", "\0", "^", "&", "*") if x in resp], resp
        assert resp == expected, resp

    def test_safe_good_path(self):
        path = "/var/lib/test/path/filename.txt"
        resp = reuse.safe_path(path)
        assert resp == path, resp

    def test_sorting(self):
        al = [{"name": "a"}, {"name": "c"}, {"name": "b"}]
        resp = reuse.sort_by(al, "name")
        assert resp[0]['name'] == 'a'
        assert resp[1]['name'] == 'b'
        assert resp[2]['name'] == 'c'

    def test_type_errors(self):
        self.assertRaises(TypeError, reuse.config_dict, dict(config='1'))
        self.assertRaises(TypeError, reuse.check_filename, tuple())
        self.assertRaises(TypeError, reuse.safe_filename, set())
        self.assertRaises(TypeError, reuse.safe_path, dict())

    def test_hash_file(self):
        valid = "489abd73c49c41650a609d2eb67987b1"
        resp = reuse.file_hash(os.path.join(test_root, "test_hash"))
        assert resp == valid, (resp, valid)

    def test_bad_hash_type(self):
        self.assertRaises(ValueError, reuse.file_hash, "", hash_type="sham5")

    def test_find_files(self):
        resp = reuse.find_all_files(test_root, ext=".cfg")
        assert resp[0].endswith(os.path.join(test_root, "test_config.cfg"))

    def test_find_files_multi_ext(self):
        resp = reuse.find_all_files(test_root, ext=[".cfg", ".nope"])
        assert resp[0].endswith(os.path.join(test_root, "test_config.cfg"))

    def test_find_files_name(self):
        resp = reuse.find_all_files(test_root, name="test_config")
        assert resp[0].endswith(os.path.join(test_root, "test_config.cfg"))