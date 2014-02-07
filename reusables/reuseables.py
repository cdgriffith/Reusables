#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Chris Griffith"
__version__ = "0.0.1a"

import os
import sys

python_version = sys.version()
python_version_string = ".".join(sys.version())
package_root = os.path.abspath(os.path.dirname(__file__))
python3x = python_version >= (3, 0)
python2x = python_version < (3, 0)


def join_paths(*paths):
    path = os.path.abspath(paths[0])
    for next_path in paths[1:]:
        path = os.path.join(path, next_path)
    return path


def join_root(*paths):
    path = package_root
    for next_path in paths:
        path = os.path.join(path, next_path)
    return path


def config_dict(config_file=[], auto_find=False, **config_parser_options):
    """
    Return configuration options as dictionary. Accepts either a single
    config file or a list of files. Auto find will search for all .cfg, .config
    and .ini in the execution directory and package root (unsafe but handy).
    """

    import glob
    if python2x:
        import ConfigParser as configparser
    elif python3x:
        import configparser

    cfg_parser = configparser.ConfigParser(**config_parser_options)

    cfg_files = []

    if auto_find:
        cfg_files.extend(glob.glob("*.cfg"))
        cfg_files.extend(glob.glob("*.config"))
        cfg_files.extend(glob.glob("*.ini"))
        cfg_files.extend(join_root(glob.glob("*.cfg")))
        cfg_files.extend(join_root(glob.glob("*.config")))
        cfg_files.extend(join_root(glob.glob("*.ini")))

    if not isinstance(cfg_files, list):
        if isinstance(cfg_files, str):
            cfg_files.append(cfg_files)
        else:
            raise TypeError("config_files must be a list or a string")
    else:
        cfg_files.extend(config_file)

    cfg_parser.read(cfg_files)

    return {section: {k: v for k, v in cfg_parser.items(section)}
            for section in cfg_parser.sections()}