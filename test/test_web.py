#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import os
import reusables

test_root = os.path.abspath(os.path.dirname(__file__))
data_dr = os.path.join(test_root, "data")


class TestWeb(unittest.TestCase):

    def test_server_and_download(self):
        test_data = "Test data of a fox jumping"
        reusables.pushd(data_dr)
        with open("example_file", "w") as f:
            f.write(test_data)
        server = reusables.Server(port=9999)
        try:
            dl = reusables.download("http://localhost:9999/example_file",
                                    save_to_file=False)
            assert dl.decode("utf-8") == test_data
        finally:
            server.stop()
            os.unlink("example_file")

