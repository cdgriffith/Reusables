#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from reusables.cli import *
from .common_test_data import *


class TestCLI(BaseTestClass):

    ex = os.path.join(data_dr, "ex.txt")

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(cls.ex)
        except OSError:
            pass

    @classmethod
    def setUpClass(cls):
        with open(cls.ex, "w") as f:
            f.write("this\nis\r\nan\r\nfancy example\n file! \n")

    def test_cmd(self):
        import sys
        save_file = os.path.join(data_dr, "stdout")
        saved = sys.stdout
        sys.stdout = open(save_file, "w")
        cmd(">&2 echo 'hello'", raise_on_return=True)
        sys.stdout.close()
        sys.stdout = saved
        try:
            with open(save_file, "r") as f:
                assert "hello" in f.read()
        finally:
            os.unlink(save_file)

    def test_paths(self):
        push = pushd(data_dr)
        assert push[0] == data_dr
        assert popd()[0] == os.getcwd()
        assert popd()[0] == os.getcwd()
        assert popd()[0] == os.getcwd()
        assert pwd() == os.getcwd()
        cur = os.getcwd()
        cd(data_dr)
        assert pwd() == data_dr
        os.chdir(cur)

    def test_ls(self):
        pushd(data_dr)
        test1 = ls(printed=False)
        assert "test" in test1.decode("utf-8")
        test2 = ls()

    def test_head(self):
        lines = head(self.ex, printed=False)
        assert len(lines) == 5, len(lines)
        assert 'file!' in lines[-1], lines
        head(self.ex, printed=True)

    def test_tail(self):
        lines = tail(self.ex, lines=2, printed=False)
        assert len(lines) == 2, len(lines)
        assert 'file!' in lines[-1], lines
        tail(self.ex, printed=True)

    def test_cat(self):
        cat(self.ex)

    def test_find(self):
        assert self.ex in find(directory=data_dr)

    def test_cp(self):
        try:
            cp(self.ex, "test_file")
            cp(self.ex, "test_file")
            try:
                cp([self.ex, "test_file"], "test_file2")
            except OSError:
                pass
            else:
                raise AssertionError("Should have raised OSError")
        finally:
            os.unlink("test_file")
            try:
                os.unlink("test_file2")
            except OSError:
                pass

