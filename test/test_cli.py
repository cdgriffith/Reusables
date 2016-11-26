#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from reusables.cli import *
from .common_test_data import *


class TestCLI(BaseTestClass):

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
        pass

    def test_tail(self):
        pass

    def test_cat(self):
        pass