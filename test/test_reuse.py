#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
import tempfile
import subprocess

import reusables

from .common_test_data import *


class TestReuse(BaseTestClass):
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

    def test_get_config_dict(self):
        resp = reusables.config_dict(os.path.join(test_root, "test_config.cfg"))
        assert resp["Section1"]["key 1"] == "value 1"
        assert resp["Section 2"] == {}

    def test_get_config_dict_auto(self):
        resp = reusables.config_dict(auto_find=test_root)
        assert resp.get("Section1") == {"key 1": "value 1", "key2": "Value2"}, resp.get("Section1")

    def test_get_config_dict_no_verify(self):
        resp = reusables.config_dict("bad_loc.cfg", verify=False)
        assert resp == {}, resp

    def test_get_config_dict_multiple(self):
        resp = reusables.config_dict([os.path.join(test_root, "test_config.cfg")])
        assert resp == {"Section1": {"key 1": "value 1", "key2": "Value2"}, "Section 2": {}}, resp

    def test_get_config_namespace(self):
        resp = reusables.config_namespace(os.path.join(test_root, "test_config.cfg"))
        assert resp.Section1.key2 == "Value2", str(resp.Section1)

    def test_check_bad_filename(self):
        resp = reusables.check_filename("safeFile?.text")
        assert not resp

    def test_check_good_filename(self):
        resp = reusables.check_filename("safeFile.text")
        assert resp

    def test_safe_bad_filename(self):
        resp = reusables.safe_filename('<">ThatsNotaFileName.\0ThatsASpaceShip^&*')
        assert not [x for x in ('"', "?", "\0", "<", ">", "*") if x in resp], resp
        assert reusables.check_filename(resp)

    def test_safe_good_filename(self):
        infilename = "SafeFile.txt"
        resp = reusables.safe_filename(infilename)
        assert resp == infilename, resp

    def test_type_errors(self):
        self.assertRaises(TypeError, reusables.config_dict, dict(config="1"))
        self.assertRaises(TypeError, reusables.check_filename, tuple())
        self.assertRaises(TypeError, reusables.safe_filename, set())
        self.assertRaises(TypeError, reusables.safe_path, dict())

    def test_hash_file(self):
        valid = "81dc9bdb52d04dc20036dbd8313ed055"
        hash_file = "1234"
        with open(os.path.join(test_root, "test_hash"), "w") as out_hash:
            out_hash.write(hash_file)
        resp = reusables.file_hash(os.path.join(test_root, "test_hash"))
        os.unlink(os.path.join(test_root, "test_hash"))
        assert resp == valid, (resp, valid)

    def test_bad_hash_type(self):
        self.assertRaises(ValueError, reusables.file_hash, "", hash_type="sham5")

    def test_count_files(self):
        self._extract_structure()
        resp = reusables.count_files(test_root, ext=".cfg")
        assert resp == 1, resp

    def test_count_name(self):
        self._extract_structure()
        resp = reusables.count_files(test_root, name="file_")
        assert resp == 4, reusables.find_files_list(test_root, name="file_", abspath=True)

    def test_fail_count_files(self):
        self._extract_structure()
        try:
            reusables.count_files(test_root, ext={"ext": ".cfg"})
        except TypeError:
            pass
        else:
            raise AssertionError("Should raise type error")

    def test_find_files(self):
        resp = reusables.find_files_list(test_root, ext=".cfg", abspath=True, disable_pathlib=True)
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_find_files_multi_ext(self):
        resp = reusables.find_files_list(test_root, ext=[".cfg", ".nope"], disable_pathlib=True)
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_find_files_name(self):
        resp = reusables.find_files_list(test_root, name="test_config", disable_pathlib=True)
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_find_files_bad_ext(self):
        resp = iter(reusables.find_files(test_root, ext={"test": ".txt"}, disable_pathlib=True))
        self.assertRaises(TypeError, next, resp)

    def test_find_file_sad_bad(self):
        try:
            reusables.find_files_list(name="*.*", match_case=True)
        except ValueError:
            pass
        else:
            raise AssertionError("Cant do that")

    def test_find_files_depth(self):
        self._extract_structure()
        resp = reusables.find_files_list(test_structure, depth=1)
        assert not resp, resp
        resp2 = reusables.find_files_list(test_structure, depth=2)
        assert len(resp2) == 5, resp2

    def test_find_files_iterator(self):
        resp = reusables.find_files(test_root, ext=".cfg", disable_pathlib=True)
        assert not isinstance(resp, list)
        resp = [x for x in resp]
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_path_single(self):
        resp = reusables.safe_path("path")
        assert resp == "path", resp

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

    def test_extract(self):
        assert os.path.exists(test_structure_tar)
        reusables.extract(test_structure_tar, path=test_root, delete_on_success=False)
        assert os.path.exists(test_structure)
        assert os.path.isdir(test_structure)
        shutil.rmtree(test_structure)

    def test_extract_zip(self):
        assert os.path.exists(test_structure_zip)
        reusables.extract(test_structure_zip, path=test_root, delete_on_success=False)
        assert os.path.exists(test_structure)
        assert os.path.isdir(test_structure)
        shutil.rmtree(test_structure)

    def test_extract_rar(self):
        if reusables.win_based:
            import rarfile

            rarfile.UNRAR_TOOL = os.path.abspath(os.path.join(test_root, "UnRAR.exe"))
        assert os.path.exists(test_structure_rar)
        reusables.extract(test_structure_rar, path=test_root, delete_on_success=False, enable_rar=True)
        assert os.path.exists(test_structure)
        assert os.path.isdir(test_structure)
        shutil.rmtree(test_structure)

    def test_extract_bad(self):
        self._extract_structure()
        path = os.path.join(test_structure, "Files", "file_1")
        assert os.path.exists(path)
        try:
            reusables.extract(path, path=test_root, delete_on_success=False)
        except TypeError:
            pass
        else:
            raise AssertionError("Extracted a bad file?")

    def test_extract_empty(self):
        empt = tempfile.mktemp()
        open(empt, "a").close()
        try:
            reusables.extract(empt)
            assert False, "Should have failed"
        except OSError:
            assert True
        os.unlink(empt)

    def test_auto_delete(self):
        tmpdir = tempfile.mkdtemp()
        fname = tmpdir + "test.zip"
        shutil.copy(test_structure_zip, fname)
        reusables.extract(fname, path=tmpdir, delete_on_success=True)
        assert not os.path.exists(fname)
        shutil.rmtree(tmpdir)

    def test_os_tree(self):
        dir = tempfile.mkdtemp(suffix="dir1")
        dir2 = tempfile.mkdtemp(suffix="dir2", dir=dir)
        without_files = reusables.os_tree(dir)
        answer = {dir.replace(tempfile.tempdir, "", 1).lstrip(os.sep): {dir2.lstrip(dir).lstrip(os.sep): {}}}
        assert without_files == answer, "{0} != {1}".format(without_files, answer)

    def test_os_tree_bad_dir(self):
        lol_Im_not_a_dir = open("fake_dir", "w")
        try:
            reusables.os_tree("fake_dir")
        except OSError:
            return True
        else:
            assert False
        finally:
            lol_Im_not_a_dir.close()
            os.unlink("fake_dir")

    def test_os_tree_no_dir(self):
        try:
            reusables.os_tree("I am pretty sure this directory does not exist, at least I hope not, dear goodness")
        except OSError:
            return True
        else:
            assert False

    def test_bad_file_hash_type(self):
        try:
            reusables.file_hash("test_file", hash_type="There is no way this is a valid hash type")
        except ValueError:
            return True
        else:
            assert False

    def test_csv(self):
        matrix = [
            ["Date", "System", "Size", "INFO"],
            ["2016-05-10", "MAIN", 456, [1, 2]],
            ["2016-06-11", "SECONDARY", 4556, 66],
        ]
        afile = reusables.join_paths(test_root, "test.csv")
        try:
            reusables.list_to_csv(matrix, afile)
            from_save = reusables.csv_to_list(afile)
        finally:
            try:
                os.unlink(afile)
            except OSError:
                pass

        assert len(from_save) == 3
        assert from_save[0] == ["Date", "System", "Size", "INFO"], from_save[0]
        assert from_save[1] == ["2016-05-10", "MAIN", "456", "[1, 2]"], from_save[1]
        assert from_save[2] == ["2016-06-11", "SECONDARY", "4556", "66"], from_save[2]

    def test_json_save(self):
        test_data = {"Hello": ["how", "are"], "You": "?", "I'm": True, "fine": 5}
        afile = reusables.join_paths(test_root, "test.json")
        try:
            reusables.save_json(test_data, afile)
            out_data = reusables.load_json(afile)
        finally:
            try:
                os.unlink(afile)
            except OSError:
                pass

        assert out_data == test_data

    def test_dup_empty(self):
        empty_file = reusables.join_paths(test_root, "empty")
        reusables.touch(empty_file)
        self._extract_structure()
        b = [x for x in reusables.dup_finder(empty_file, test_root)]
        print(b)

    def test_config_reader(self):
        cfg = reusables.config_namespace(reusables.join_paths(test_root, "data", "test_config.ini"))

        assert isinstance(cfg, reusables.ConfigNamespace)
        assert cfg.General.example == "A regular string"

        assert cfg["Section 2"].list("exampleList", mod=lambda x: int(x)) == [234, 123, 234, 543]

    def test_config_reader_bad(self):
        try:
            cfg = reusables.config_namespace(reusables.join_paths(test_root, "data", "test_bad_config.ini"))
        except AttributeError:
            pass
        else:
            assert False

    def test_run(self):
        cl = reusables.run("echo test", shell=True, stderr=None, copy_local_env=True)
        try:
            cl.check_returncode()
        except subprocess.CalledProcessError:
            pass
        assert cl.stdout == (b"test\n" if reusables.nix_based else b"test\r\n"), cl
        import platform

        outstr = "CompletedProcess(args='echo test', returncode=0{2}, stdout={0}'test{1}\\n')".format(
            "b" if reusables.PY3 else "",
            "\\r" if reusables.win_based else "",
            "L" if reusables.win_based and platform.python_implementation() == "PyPy" else "",
        )

        assert str(cl) == outstr, "{0} != {1}".format(str(cl), outstr)

        try:
            cl2 = reusables.run("echo test", shell=True, timeout=5)
        except NotImplementedError:
            if reusables.PY3:
                raise AssertionError("Should only happen on PY2")
            pass
        else:
            if reusables.PY2:
                raise AssertionError("Timeout should not have worked for PY2")

        cl3 = reusables.run("exit 1", shell=True)
        try:
            cl3.check_returncode()
        except subprocess.CalledProcessError:
            pass
        else:
            assert False

    def test_dups(self):
        self._extract_structure()
        empty = os.path.join(data_dr, "empty")
        something = os.path.join(data_dr, "full")
        reusables.touch(empty)
        with open(something, "w") as f:
            f.write("stuff in here")
        try:
            dups = list(reusables.dup_finder(empty, data_dr))
            assert len(dups) == 1, dups
            dups2 = list(reusables.dup_finder(something, data_dr))
            assert len(dups2) == 1, dups
        finally:
            os.unlink(something)
            os.unlink(empty)

    def test_cut(self):

        a = reusables.cut("abcdefghi")
        assert a == ["ab", "cd", "ef", "gh", "i"]

        try:
            reusables.cut("abcdefghi", 2, "error")
        except IndexError:
            pass
        else:
            raise AssertionError("cut failed")

        b = reusables.cut("abcdefghi", 2, "remove")
        assert b == ["ab", "cd", "ef", "gh"]

        c = reusables.cut("abcdefghi", 2, "combine")
        assert c == ["ab", "cd", "ef", "ghi"]

    def test_find_glob(self):
        resp = reusables.find_files_list(test_root, name="*config*")
        assert len(resp) == 3, resp

    def test_archive(self):
        p1 = reusables.archive("data", overwrite=True)
        assert p1.endswith("archive.zip")
        assert os.path.exists(p1)
        try:
            p1 = reusables.archive("data")
        except OSError:
            pass
        else:
            raise AssertionError("Should complain about overwrite")
        finally:
            os.unlink(p1)

        p2 = reusables.archive("__init__.py", name="archive.tar")
        assert p2.endswith("archive.tar")
        assert os.path.exists(p2)
        os.unlink(p2)
        p3 = reusables.archive("__init__.py", name="archive.gz")
        assert p3.endswith("archive.gz")
        assert os.path.exists(p3)
        os.unlink(p3)
        p4 = reusables.archive("__init__.py", name="archive.bz2")
        assert p4.endswith("archive.bz2")
        assert os.path.exists(p4)
        os.unlink(p4)

    def test_bad_archive_type(self):
        try:
            reusables.archive("__init__.py", archive_type="rar")
        except ValueError:
            pass
        else:
            raise AssertionError("Should raise value error about archive_type")

        try:
            reusables.archive("__init__.py", "asdf.gah")
        except ValueError:
            pass
        else:
            raise AssertionError("You cant figure out that archive type ")

    def test_duplicate_dir(self):
        dups = reusables.directory_duplicates(test_root)
        assert len(dups) == 1, len(dups)

    def test_find_with_scandir(self):
        resp = reusables.find_files_list(test_root, ext=[".cfg", ".nope"], enable_scandir=True, disable_pathlib=True)
        assert [x for x in resp if x.endswith(os.path.join(test_root, "test_config.cfg"))]

    def test_remove_with_scandir(self):
        self._extract_structure()
        delete = reusables.remove_empty_directories(test_structure, enable_scandir=True)
        assert len(delete) == 8, (len(delete), delete)
        assert not [x for x in delete if "empty" not in x.lower()]
        self._remove_structure()

    def test_find_file_pathlib(self):
        if reusables.python_version >= (3, 4):
            import pathlib

            files = reusables.find_files_list(test_root, ext=".cfg", abspath=True)
            assert isinstance(files[0], pathlib.Path)
            files2 = reusables.find_files_list(test_root, ext=".cfg", abspath=True, disable_pathlib=True)
            assert not isinstance(files2[0], pathlib.Path)

    def test_sync_dirs(self):
        if reusables.python_version >= (3, 4):
            pass
        files = reusables.find_files_list(test_root, ext=".cfg", abspath=True)


if reusables.nix_based:

    class TestReuseLinux(unittest.TestCase):
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

        def test_join_path_clean(self):
            resp = reusables.join_paths("/test/", "clean/", "path")
            assert resp == "/test/clean/path", resp

        def test_join_path_dirty(self):
            resp = reusables.join_paths("/test/", "/dirty/", " path.file ")
            assert resp == "/test/dirty/path.file", resp

        def test_join_path_clean_strict(self):
            resp = reusables.join_paths("/test/", "clean/", "path/")
            assert resp == "/test/clean/path/", resp

        def test_join_here(self):
            resp = reusables.join_here("clean/")
            path = os.path.abspath(os.path.join(".", "clean/"))
            assert resp == path, (resp, path)


if reusables.win_based:

    class TestReuseWindows(unittest.TestCase):
        # Windows based path tests

        def test_win_join_path_clean(self):
            resp = reusables.join_paths("C:\\test", "clean\\", "path").rstrip("\\")
            assert resp == "C:\\test\\clean\\path", resp

        def test_win_join_path_dirty(self):
            resp = reusables.join_paths("C:\\test\\", "D:\\dirty", " path.file ")
            assert resp == "D:\\dirty\\path.file", resp

        def test_win_join_here(self):
            resp = reusables.join_here("clean\\")
            path = os.path.abspath(os.path.join(".", "clean\\"))
            assert resp == path, (resp, path)

        def test_cant_delete_empty_file(self):
            dir = tempfile.mkdtemp(suffix="a_dir")
            tf = os.path.join(dir, "test_file")
            file = open(tf, "w")
            try:
                os.chmod(tf, 0o444)
            except Exception:
                pass

            try:
                reusables.remove_empty_files(dir, ignore_errors=False)
            except OSError:
                return True
            else:
                assert False
            finally:
                file.close()

        def test_cant_delete_empty_file_ignore_errors(self):
            dir = tempfile.mkdtemp(suffix="a_dir")
            file = open(os.path.join(dir, "test_file"), "w")
            try:
                reusables.remove_empty_files(dir, ignore_errors=True)
            finally:
                file.close()


if __name__ == "__main__":
    unittest.main()
