#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import os

import reusables
from reusables.cli import popd, pushd
from .common_test_data import BaseTestClass, data_dr


class TestWeb(BaseTestClass):
    def test_server_and_download(self):
        try:
            os.unlink("example_file")
        except OSError:
            pass
        try:
            os.unlink("dlfile")
        except OSError:
            pass

        port = random.randint(9000, 9999)

        test_data = "Test data of a fox jumping"
        pushd(data_dr)
        with open("example_file", "w") as f:
            f.write(test_data)

        server = reusables.ThreadedServer(port=port)
        try:
            dl = reusables.download("http://localhost:{0}/example_file".format(port), save_to_file=False)
            assert dl.decode("utf-8") == test_data
            dl2 = reusables.download("http://localhost:{0}/example_file".format(port))
            assert not dl2
            dl3 = reusables.download("http://localhost:{0}/example_file".format(port), filename="dlfile")
            assert dl3
            with open("dlfile", "r") as f:
                f.read() == test_data
        finally:
            server.stop()
            try:
                os.unlink("example_file")
            except OSError:
                pass
            try:
                os.unlink("dlfile")
            except OSError:
                pass
            popd()

    def test_bad_url(self):
        try:
            reusables.download("codecalamity.com", save_to_file=False)
        except ValueError:
            pass
        else:
            assert False

    # def test_url_to_ip(self):
    #     assert len(reusables.url_to_ip("codecalamity.com").split(".")) == 4
    #     assert not reusables.url_to_ip("9999999999999999999")
    #
    # def test_url_to_ips(self):
    #     assert len(reusables.url_to_ips("codecalamity.com")[0].split(".")) == 4
    #     assert not reusables.url_to_ips("9999999999999999999")

    # def test_ip_to_url(self):
    #     assert "google" in reusables.ip_to_url("8.8.8.8")
    #     assert not reusables.ip_to_url("codecalamity.com")
