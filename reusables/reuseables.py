#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Chris Griffith"
__version__ = "0.0.2"

import os
import sys
import re

python_version = sys.version_info[0:3]
python_version_string = ".".join([str(x) for x in python_version])
package_root = os.path.abspath(os.path.dirname(__file__))
python3x = python_version >= (3, 0)
python2x = python_version < (3, 0)
regex = {"safe_filename": re.compile(r'^[\w\d\. _\-]+$')}


def join_paths(*paths):
    """
    Join multiple paths together and return the absolute path of them.
    """
    path = os.path.abspath(paths[0])
    for next_path in paths[1:]:
        path = os.path.join(path, next_path)
    return path


def join_root(*paths):
    """
    Join any path or paths as a sub directory of the current file's directory.
    """
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

    #TODO add verify path option
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


def sort_by(unordered_list, key):
    """
    Sort a list of dicts, tuples or lists by the provided dict key, or list/
    tuple position.
    """
    return sorted(unordered_list, key=lambda x: x[key])


def check_filename(filename):
    """
    Returns a boolean stating if the filename is safe to use or not.
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    if regex['safe_filename'].search(filename):
        return True
    return False


def safe_filename(filename):
    """
    Replace bad filename characters with underscores.
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    if check_filename(filename):
        return filename
    safe_name = ""
    for char in filename:
        safe_name += char if regex['safe_filename'].search(char) else "_"
    return safe_name