#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))

class TestReuse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config_file = """[Section1]
key 1 = value 1
Key2 = Value2

[Section 2]
"""
        with open(os.path.join(test_root, "test_config.cfg"), "w") as oc:
            oc.write(config_file)

    @classmethod
    def tearDownClass(cls):
        os.unlink(os.path.join(test_root, "test_config.cfg"))

    def test_join_path_clean(self):
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        resp = reusables.join_paths('/test/', 'clean/', 'path')
        assert resp == '/test/clean/path/', resp

    def test_join_path_dirty(self):
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        resp = reusables.join_paths('/test/', '/dirty/', ' path.file ')
        assert resp == '/test/dirty/path.file', resp

    def test_join_path_clean_strict(self):
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        resp = reusables.join_paths('/test/', 'clean/', 'path/', strict=True)
        assert resp == '/test/clean/path/', resp

    def test_join_path_dirty_strict(self):
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        resp = reusables.join_paths('/test/', '/dirty/',
                                    ' path.file ', strict=True)
        assert resp == '/dirty/ path.file ', resp

    def test_join_root(self):
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        resp = reusables.join_root('clean/')
        path = os.path.abspath(os.path.join(".", 'clean/'))
        assert resp == path, (resp, path)

    def test_get_config_dict(self):
        resp = reusables.config_dict(os.path.join(test_root, 'test_config.cfg'))
        assert resp['Section1']['key 1'] == 'value 1'
        assert resp['Section 2'] == {}

    def test_get_config_dict_auto(self):
        resp = reusables.config_dict(auto_find=True)
        assert resp.get('Section1') == {'key 1': 'value 1', 'key2': 'Value2'}

    def test_get_config_dict_no_verify(self):
        resp = reusables.config_dict('bad_loc.cfg', verify=False)
        assert resp == {}, resp

    def test_get_config_dict_multiple(self):
        resp = reusables.config_dict([os.path.join(test_root, 'test_config.cfg')])
        assert resp == {'Section1': {'key 1': 'value 1', 'key2': 'Value2'}, 'Section 2': {}}, resp

    def test_get_config_namespace(self):
        resp = reusables.config_namespace(os.path.join(test_root,
                                                   'test_config.cfg'))
        assert resp.Section1.key2 == 'Value2', str(resp.Section1)

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
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        path = "/var/lib\\/test/p?!ath/fi\0lename.txt"
        expected = "/var/lib_/test/p__ath/fi_lename.txt"
        resp = reusables.safe_path(path)
        assert not [x for x in ("!", "?", "\0", "^", "&", "*") if x in resp], resp
        assert resp == expected, resp

    def test_safe_good_path(self):
        if not reusables.nix_based:
            self.skipTest("Linux based test")
        path = "/var/lib/test/path/filename.txt"
        resp = reusables.safe_path(path)
        assert resp == path, resp

    def test_sorting(self):
        al = [{"name": "a"}, {"name": "c"}, {"name": "b"}]
        resp = reusables.sort_by(al, "name")
        assert resp[0]['name'] == 'a'
        assert resp[1]['name'] == 'b'
        assert resp[2]['name'] == 'c'

    def test_type_errors(self):
        self.assertRaises(TypeError, reusables.config_dict, dict(config='1'))
        self.assertRaises(TypeError, reusables.check_filename, tuple())
        self.assertRaises(TypeError, reusables.safe_filename, set())
        self.assertRaises(TypeError, reusables.safe_path, dict())

    def test_hash_file(self):
        valid = "81dc9bdb52d04dc20036dbd8313ed055"
        hash_file = "1234"
        with open(os.path.join(test_root, "test_hash"), 'w') as out_hash:
            out_hash.write(hash_file)
        resp = reusables.file_hash(os.path.join(test_root, "test_hash"))
        os.unlink(os.path.join(test_root, "test_hash"))
        assert resp == valid, (resp, valid)


    def test_bad_hash_type(self):
        self.assertRaises(ValueError, reusables.file_hash, "", hash_type="sham5")

    def test_find_files(self):
        resp = reusables.find_all_files(test_root, ext=".cfg")
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_find_files_multi_ext(self):
        resp = reusables.find_all_files(test_root, ext=[".cfg", ".nope"])
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_find_files_name(self):
        resp = reusables.find_all_files(test_root, name="test_config")
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_find_files_bad_ext(self):
        resp = iter(reusables.find_all_files_generator(test_root,
                                                   ext={'test': '.txt'}))
        self.assertRaises(TypeError, next, resp)

    def test_find_files_iterator(self):
        resp = reusables.find_all_files_generator(test_root, ext=".cfg")
        assert not isinstance(resp, list)
        resp = [x for x in resp]
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_main(self):
        reusables.main(["--safe-filename", "tease.txt", "--safe-path", "/var/lib"])

    def test_namespace(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        namespace = reusables.Namespace(**test_dict)
        assert namespace.key1 == test_dict['key1']
        assert dict(getattr(namespace, 'Key 2')) == test_dict['Key 2']
        setattr(namespace, 'TEST_KEY', 'VALUE')
        assert namespace.TEST_KEY == 'VALUE'
        delattr(namespace, 'TEST_KEY')
        assert 'TEST_KEY' not in namespace.to_dict()
        assert isinstance(namespace['Key 2'].Key4, reusables.Namespace)
        assert "'key1': 'value1'" in str(namespace)
        assert repr(namespace).startswith("<Namespace:")

if __name__ == "__main__":
    unittest.main()