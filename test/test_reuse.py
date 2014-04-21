#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import shutil
import tarfile
import tempfile
import datetime
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))

test_structure_tar = os.path.join(test_root, "test_structure.tar.gz")
test_structure_zip = os.path.join(test_root, "test_structure.zip")
test_structure = os.path.join(test_root, "test_structure")


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
        if os.path.exists(test_structure):
            shutil.rmtree(test_structure)

    @classmethod
    def tearDownClass(cls):
        os.unlink(os.path.join(test_root, "test_config.cfg"))
        if os.path.exists(test_structure):
            shutil.rmtree(test_structure)

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
        resp = reusables.safe_filename("<\">ThatsNotaFileName.\0ThatsASpaceShip^&*")
        assert not [x for x in ("\"", "?", "\0", "<", ">", "*") if x in resp], resp
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
        reusables.main(["--safe-filename",
                        "tease.txt",
                         "--safe-path",
                        "/var/lib"])

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

    def test_namespace_tree(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        namespace = reusables.Namespace(**test_dict)
        result = namespace.tree_view(sep="    ")
        assert result.startswith("key1\n") or result.startswith("Key 2\n")
        assert "Key4" in result and "    Value5\n" not in result

    def test_path_single(self):
        resp = reusables.safe_path('path')
        assert resp == 'path', resp

    def _extract_structure(self):
        tar = tarfile.open(test_structure_tar)
        tar.extractall(path=test_root)
        tar.close()
        assert os.path.exists(test_structure)
        assert os.path.isdir(test_structure)

    def _remove_structure(self):
        shutil.rmtree(test_structure)
        assert not os.path.exists(test_structure)

    def test_remove_directories(self):
        self._extract_structure()
        delete = reusables.remove_empty_directories(test_structure)
        assert len(delete) == 8, (len(delete), delete)
        assert not [x for x in delete if "empty" not in x.lower()]
        self._remove_structure()

    def test_remove_files(self):
        self._extract_structure()
        delete = reusables.remove_empty_files(test_structure)
        assert len(delete) == 3, (len(delete), delete)
        assert not [x for x in delete if "file" not in x.lower()]
        self._remove_structure()

    def test_extract_all(self):
        assert os.path.exists(test_structure_tar)
        reusables.extract_all(test_structure_tar, path=test_root, dnd=True)
        assert os.path.exists(test_structure)
        assert os.path.isdir(test_structure)
        shutil.rmtree(test_structure)

    def test_extract_all_zip(self):
        assert os.path.exists(test_structure_zip)
        reusables.extract_all(test_structure_zip, path=test_root, dnd=True)
        assert os.path.exists(test_structure)
        assert os.path.isdir(test_structure)
        shutil.rmtree(test_structure)

    def test_extract_empty(self):
        empt = tempfile.mktemp()
        open(empt, "a").close()
        try:
            reusables.extract_all(empt)
            assert False, "Should have failed"
        except OSError:
            assert True
        os.unlink(empt)

    def test_auto_delete(self):
        tmpdir = tempfile.mkdtemp()
        fname = tmpdir + "test.zip"
        shutil.copy(test_structure_zip, fname)
        reusables.extract_all(fname, path=tmpdir, dnd=False)
        assert not os.path.exists(fname)
        shutil.rmtree(tmpdir)

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
        assert now.format("{hour}:{minute}:{second}") == now.strftime("%I:%M:%S"), (now.strftime("%I:%M:%S"), now.format("{hour}:{minute}:{second}"))
        assert now.format("{hour}:{minute}:{hour}:{24hour}:{24-hour}") == now.strftime("%I:%M:%I:%H:%H"), now.format("{hour}:{minute}:{hour}:{24hour}:{24-hour}")

    def test_os_tree(self):
        dir = tempfile.mkdtemp(suffix="dir1")
        dir2 = tempfile.mkdtemp(suffix="dir2", dir=dir)
        without_files = reusables.os_tree(dir)
        answer = {dir.replace(tempfile.tempdir, "", 1).lstrip(os.sep): {dir2.lstrip(dir).lstrip(os.sep): {}}}
        assert without_files == answer, "{0} != {1}".format(without_files, answer)

    def test_namespace_from_dict(self):
        ns = reusables.Namespace.from_dict({"k1": "v1", "k2": {"k3": "v2"}})
        assert ns.k2.k3 == "v2"

    def test_namespace_from_bad_dict(self):
        try:
            ns = reusables.Namespace.from_dict('{"k1": "v1", "k2": {"k3": "v2"}}')
        except TypeError:
            assert True
        else:
            assert False, "Should have raised type error"

    def test_datetime_from_iso(self):
        import datetime
        test = datetime.datetime.now()
        testiso = test.isoformat()
        dt = reusables.DateTime.from_iso(testiso)
        assert dt.hour == dt.hour
        assert test == dt
        assert isinstance(dt, reusables.DateTime)

    def test_datetime_from_bad_iso(self):
        try:
            reusables.DateTime.from_iso("hehe not a real time")
        except TypeError:
            assert True
        else:
            assert False, "How is that a datetime???"

if reusables.win_based:
    class TestReuseWindows(unittest.TestCase):
            # Windows based path tests

        def test_win_join_path_clean(self):
            resp = reusables.join_paths('C:\\test', 'clean\\', 'path')
            assert resp == 'C:\\test\\clean\\path', resp

        def test_win_join_path_dirty(self):
            resp = reusables.join_paths('C:\\test\\', 'D:\\dirty', ' path.file ')
            assert resp == 'D:\\dirty\\path.file', resp

        def test_win_join_path_clean_strict(self):
            resp = reusables.join_paths('C:\\test', 'clean\\', 'path', strict=True)
            assert resp == 'C:\\test\\clean\\path', resp

        def test_win_join_path_dirty_strict(self):
            resp = reusables.join_paths('C:\\test\\', 'D:\\dirty',
                                        ' path.file ', strict=True)
            assert resp == 'D:\\dirty\\ path.file ', resp

        def test_win_join_root(self):
            if not reusables.win_based:
                self.skipTest("Windows based test")
            resp = reusables.join_root('clean\\')
            path = os.path.abspath(os.path.join(".", 'clean\\'))
            assert resp == path, (resp, path)

if __name__ == "__main__":
    unittest.main()