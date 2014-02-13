#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Reusables - Commonly Consumed Code Chunks

Copyright (c) 2014  - Chris Griffith - MIT License
"""
__author__ = "Chris Griffith"
__version__ = "0.0.5"

import os
import sys
import re
import logging

python_version = sys.version_info[0:3]
version_string = ".".join([str(x) for x in python_version])
package_root = os.path.abspath(os.path.dirname(__file__))
python3x = python_version >= (3, 0)
python2x = python_version < (3, 0)
regex = {"safe_filename": re.compile(r'^[\w\d\. _\-\(\)]+$'),
         "safe_path_windows": re.compile(r'^[\w\d _\-\\\(\)]+$'),
         "safe_path_nix": re.compile(r'^[\w\d\. _\-/\(\)]+$')}
nix_based = os.name == "posix"
win_based = os.name == "nt"
logger = logging.getLogger(__name__)
if python_version >= (2, 7):
    #Surpresses warning that no logger is found if a parent logger is not set
    logger.addHandler(logging.NullHandler())


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def join_paths(*paths, **kwargs):
    """
    Join multiple paths together and return the absolute path of them.
    """
    path = os.path.abspath(paths[0])
    for next_path in paths[1:]:
        next_path = next_path.lstrip(os.sep).strip() if not \
            kwargs.get('strict') else next_path
        path = os.path.join(path, next_path)
    if (not kwargs.get('strict') and
            "." not in os.path.basename(path) and
            not path.endswith(os.sep)):
        path += os.sep
    return path


def join_root(*paths, **kwargs):
    """
    Join any path or paths as a sub directory of the current file's directory.
    """
    path = package_root
    for next_path in paths:
        next_path = next_path.lstrip(os.sep).strip() if not \
            kwargs.get('strict') else next_path
        path = os.path.join(path, next_path)
    return path


def config_dict(config_file=None, auto_find=False, verify=True, **cfg_options):
    """
    Return configuration options as dictionary. Accepts either a single
    config file or a list of files. Auto find will search for all .cfg, .config
    and .ini in the execution directory and package root (unsafe but handy).
    """
    if not config_file: config_file = []
    import glob
    if python2x:
        import ConfigParser as configparser
    elif python3x:
        import configparser

    cfg_parser = configparser.ConfigParser(**cfg_options)

    cfg_files = []

    if config_file:
        if not isinstance(config_file, list):
            if isinstance(config_file, str):
                cfg_files.append(config_file)
            else:
                raise TypeError("config_files must be a list or a string")
        else:
            cfg_files.extend(config_file)
    else:
        auto_find = True

    if auto_find:
        cfg_files.extend(find_all_files(".", ext=(".cfg", ".config", ".ini")))
        cfg_files.extend(find_all_files(package_root,
                                        ext=(".cfg", ".config", ".ini")))

    if verify:
        cfg_parser.read([cfg for cfg in cfg_files if os.path.exists(cfg)])
    else:
        cfg_parser.read(cfg_files)

    return {section: {k: v for k, v in cfg_parser.items(section)}
            for section in cfg_parser.sections()}


def config_namespace(config_file=None, auto_find=False,
                     verify=True, **cfg_options):
    return Namespace(**config_dict(config_file, auto_find,
                                   verify, **cfg_options))

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


def safe_filename(filename, replacement="_"):
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
        safe_name += char if regex['safe_filename'].search(char) \
            else replacement
    return safe_name


def safe_path(path, replacement="_"):
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
    if win_based and dirname.find(":\\") == 1 and dirname[0].isalpha():
        safe_dirname = dirname[0:3]
        dirname = dirname[3:]
    if regexp.search(dirname) and check_filename(filename):
        return path
    else:
        for char in dirname:
            safe_dirname += char if regexp.search(char) else replacement
    sanitized_path = os.path.normpath("{path}{sep}{filename}".format(
        path=safe_dirname,
        sep=os.sep if not safe_dirname.endswith(os.sep) else "",
        filename=filename))
    if (not filename and
            path.endswith(os.sep) and
            not sanitized_path.endswith(os.sep)):
        sanitized_path += os.sep
    return sanitized_path


def file_hash(path, hash_type="md5", blocksize=65536):
    """
    Hash a given file with sha256 and return the hex digest.

    This function is designed to be non memory intensive.
    """
    import hashlib
    hashes = {"md5": hashlib.md5,
              "sha1": hashlib.sha1,
              "sha256": hashlib.sha256,
              "sha512": hashlib.sha512}
    if hash_type not in hashes:
        raise ValueError("Hash type must be: md5, sha1, sha256, or sha512")
    hasher = hashes[hash_type]()
    with open(path, "rb") as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.hexdigest()


def find_all_files(directory, ext=None, name=None):
    file_list = []
    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if ext:
                for end in ext:
                    if file.endswith(end):
                        break
                else:
                    continue
            if name:
                if name not in file:
                    continue
            file_list.append(join_paths(root, file))
    return file_list


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="reuse")
    parser.add_argument("--safe-filename", dest="filename", action='append',
                        help="Verify a filename contains only letters, numbers,\
spaces, hyphens, underscores and periods")
    parser.add_argument("--safe-path", dest="path", action='append',
                        help="Verify a path contains only letters, numbers,\
spaces, hyphens, underscores, periods (unix), separator, and drive (win)")
    args = parser.parse_args()
    if args.filename:
        for filename in args.filename:
            print(safe_filename(filename))
    if args.path:
        for path in args.path:
            print(safe_path(path))


if __name__ == "__main__":
    main()