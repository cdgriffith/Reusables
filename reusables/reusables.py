#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Chris Griffith"
__version__ = "0.0.3"

import os
import sys
import re
import logging

python_version = sys.version_info[0:3]
python_version_string = ".".join([str(x) for x in python_version])
package_root = os.path.abspath(os.path.dirname(__file__))
python3x = python_version >= (3, 0)
python2x = python_version < (3, 0)
regex = {"safe_filename": re.compile(r'^[\w\d\. _\-]+$'),
         "safe_path_windows": re.compile(r'^[\w\d _\-\\]+$'),
         "safe_path_nix": re.compile(r'^[\w\d\. _\-/]+$')}
nix_based = os.name == "posix"
win_based = os.name == "nt"
verbose = False
_will_log = False
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def _log(msg, level=logging.INFO):
    if verbose:
        print(msg)
    if logging:
        logging.log(level, msg)


def enable_logging():
    """
    Turn on logging.
    """
    global _will_log
    _will_log = True
    _log("Logging enabled")


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


def config_dict(config_file=[], auto_find=False, verify=True, **cfg_options):
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

    cfg_parser = configparser.ConfigParser(**cfg_options)

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

    if verify:
        for cfg in cfg_files:
            if not os.path.exists(cfg):
                _log("Config file not found: {0}".format(cfg))
                cfg_files.pop(cfg)

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
    Returns a boolean stating if the filename is safe to use or not. Note that
    this does not test for "legal" names accepted, but a more restricted set of:
    Letters, numbers, spaces, hyphens, underscores and periods
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    if regex['safe_filename'].search(filename):
        return True
    return False


def safe_filename(filename):
    """
    Replace unsafe filename characters with underscores. Note that this does not
    test for "legal" names accepted, but a more restricted set of:
    Letters, numbers, spaces, hyphens, underscores and periods
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    if regex['safe_filename'].search(filename):
        return filename
    safe_name = ""
    for char in filename:
        safe_name += char if regex['safe_filename'].search(char) else "_"
    return safe_name


def safe_path(path):
    """
    Replace unsafe path characters with underscores. Note that this does not
    test for "legal" characters, but a more restricted set of:
    Letters, numbers, space, hyphen, underscore, period, separator, and drive

    Supports windows and *nix systems.
    """
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    filename = safe_filename(os.path.basename(path))
    dirname = os.path.dirname(path)
    safe_dirname = ""
    regexp = regex['safe_path_windows'] if win_based else regex['safe_path_nix']
    if dirname.find(":\\") == 1 and dirname[0].isalpha():
        dirname = dirname[3:]
        safe_dirname = dirname[0:3]
    if regexp.search(dirname):
        safe_dirname += dirname
    else:
        for char in dirname:
            safe_dirname += char if regexp.search(char) else "_"
    sanitized_path = os.path.normpath("{path}{sep}{filename}".format(
        path=safe_dirname,
        sep=os.sep if not safe_dirname.endswith(os.sep) else "",
        filename=filename))
    if (not filename and
            path.endswith(os.sep) and
            not sanitized_path.endswith(os.sep)):
        sanitized_path += os.sep
    return sanitized_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="reusables")
    parser.add_argument("--safe-filename", dest="filename", action='append',
                        help="Verify a filename contains only letters, numbers,\
spaces, hyphens, underscores and periods")
    parser.add_argument("--safe-path", dest="path", action='append',
                        help="Verify a path contains only letters, numbers,\
spaces, hyphens, underscores, periods (unix), separator, and drive (win)")
    args = parser.parse_args()
    print(args)
    if args.filename:
        for filename in args.filename:
            print(safe_filename(filename))
    if args.path:
        for path in args.path:
            print(safe_path(path))