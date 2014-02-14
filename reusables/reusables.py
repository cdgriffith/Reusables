#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Reusables - Commonly Consumed Code Commodities

Copyright (c) 2014  - Chris Griffith - MIT License
"""
__author__ = "Chris Griffith"
__version__ = "0.1.3"

import os
import sys
import re
import logging

python_version = sys.version_info[0:3]
version_string = ".".join([str(x) for x in python_version])
package_root = os.path.abspath(os.path.dirname(__file__))
python3x = python_version >= (3, 0)
python2x = python_version < (3, 0)
nix_based = os.name == "posix"
win_based = os.name == "nt"
logger = logging.getLogger(__name__)
if python_version >= (2, 7):
    #Surpresses warning that no logger is found if a parent logger is not set
    logger.addHandler(logging.NullHandler())

reg_exps = {"safe_filename": re.compile(r'^[\w\d\. _\-\(\)]+$'),
            "safe_path_windows": re.compile(r'^[\w\d _\-\\\(\)]+$'),
            "safe_path_nix": re.compile(r'^[\w\d\. _\-/\(\)]+$'),
            "module_attributes": re.compile(r'__([a-z]+)__ *= *[\'"](.+)[\'"]')}

common_exts = {"pictures": (".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tif",
                            ".tiff", ".ico", ".mng", ".tga", ".psd", ".xcf",
                            ".svg", ".icns"),
               "video": (".mkv", ".avi", ".mp4", ".mov", ".flv", ".mpeg",
                         ".mpg", ".3gp", ".m4v", ".ogv", ".asf", ".m1v",
                         ".m2v", ".mpe", ".ogv", ".wmv"),
               "music": (".mp3", ".ogg", ".wav", ".flac", ".aif", ".aiff",
                         ".au", ".m4a", ".wma", ".mp2", ".m4a", ".m4p", ".aac",
                         ".ra", ".mid", ".midi", ".mus", ".psf"),
               "documents": (".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt",
                             ".pptx", ".csv", ".epub", ".gdoc", ".odt", ".rtf",
                             ".txt", ".info", ".xps", ".gslides", ".gsheet"),
               "archives": (".zip", ".rar", ".7z", ".tar.gz", ".tgz", ".gz",
                            ".bzip", ".bzip2", ".bz2", ".xz", ".lzma", ".bin",
                            ".tar"),
               "cd_images": (".iso", ".nrg", ".img", ".mds", ".mdf", ".cue",
                             ".daa")}


class Namespace(dict):
    """
    Namespace container.
    Allows access to attributes by either class dot notation or item reference

    All valid:
        namespace.spam.eggs
        namespace['spam']['eggs']
        namespace['spam'].eggs
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = Namespace(**v)
            setattr(self, k, v)
        super(Namespace, self).__init__(**kwargs)

    def __contains__(self, item):
        return self.__dict__.__contains__(item)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __getattr__(self, item):
        return self.__dict__[item]

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = Namespace(**value)
        self.__dict__[key] = value

    def __delattr__(self, item):
        del self.__dict__[item]

    def __repr__(self):
        return "<Namespace: {0}>".format(str(self.to_dict()))

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self, in_dict=None):
        in_dict = in_dict if in_dict else self.__dict__
        out_dict = dict()
        for k, v in in_dict.items():
            if isinstance(v, Namespace):
                v = self.to_dict(v)
            out_dict[k] = v
        return out_dict

# Some may ask why make everything into namespaces, I ask why not
regex = Namespace(**reg_exps)
exts = Namespace(**common_exts)


def join_paths(*paths, **kwargs):
    """
    Join multiple paths together and return the absolute path of them. This
    function will 'clean' the path as well unless the option of 'strict' is
    provided.
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
    return path if kwargs.get('strict') else safe_path(path)


def join_root(*paths, **kwargs):
    """
    Join any path or paths as a sub directory of the current file's directory.
    """
    path = os.path.abspath(".")
    for next_path in paths:
        next_path = next_path.lstrip(os.sep).strip() if not \
            kwargs.get('strict') else next_path
        path = os.path.abspath(os.path.join(path, next_path))
    return path if kwargs.get('strict') else safe_path(path)


def config_dict(config_file=None, auto_find=False, verify=True, **cfg_options):
    """
    Return configuration options as dictionary. Accepts either a single
    config file or a list of files. Auto find will search for all .cfg, .config
    and .ini in the execution directory and package root (unsafe but handy).
    """
    if not config_file:
        config_file = []
    try:
        import ConfigParser as configparser
    except ImportError:
        import configparser

    cfg_parser = configparser.ConfigParser(**cfg_options)

    cfg_files = []

    if config_file:
        if not isinstance(config_file, (list, tuple)):
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

    return dict((section, dict((k, v) for (k, v) in cfg_parser.items(section)))
                for section in cfg_parser.sections())


def config_namespace(config_file=None, auto_find=False,
                     verify=True, **cfg_options):
    """
    Return configuration options as a Namespace.
    """
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
    if regex.safe_filename.search(filename):
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
    if regex.safe_filename.search(filename):
        return filename
    safe_name = ""
    for char in filename:
        safe_name += char if regex.safe_filename.search(char) \
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
    regexp = regex.safe_path_windows if win_based else regex.safe_path_nix
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
    hashit = hashes[hash_type]()
    with open(path, "rb") as infile:
        buf = infile.read(blocksize)
        while len(buf) > 0:
            hashit.update(buf)
            buf = infile.read(blocksize)
    return hashit.hexdigest()


def find_all_files_generator(directory=".", ext=None, name=None):
    """
    Walk through a file directory and return an iterator of files
    that match requirements.
    """
    print(ext)
    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if ext:
                for end in ext:
                    if file.lower().endswith(end):
                        break
                else:
                    continue
            if name:
                if name.lower() not in file.lower():
                    continue
            yield join_paths(root, file, strict=True)


def find_all_files(directory=".", ext=None, name=None):
    """
    Returns a list of all files in a sub directory that match an extension
    and or part of a filename.
    """
    return list(find_all_files_generator(directory, ext=ext, name=name))


def main(command_line_options=""):
    try:
        import argparse
    except ImportError:
        print("Cannot import argparse module, options cannot be parsed")
        return

    parser = argparse.ArgumentParser(prog="reusables")
    parser.add_argument("--safe-filename", dest="filename", action='append',
                        help="Verify a filename contains only letters, numbers,\
spaces, hyphens, underscores and periods")
    parser.add_argument("--safe-path", dest="path", action='append',
                        help="Verify a path contains only letters, numbers,\
spaces, hyphens, underscores, periods (unix), separator, and drive (win)")
    args = parser.parse_args(sys.argv if not command_line_options else
                             command_line_options)
    if args.filename:
        for filename in args.filename:
            print(safe_filename(filename))
    if args.path:
        for path in args.path:
            print(safe_path(path))


if __name__ == "__main__":
    main()