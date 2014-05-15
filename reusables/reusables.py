#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Reusables - Commonly Consumed Code Commodities

Copyright (c) 2014  - Chris Griffith - MIT License
"""
__author__ = "Chris Griffith"
__version__ = "0.2.0"

import os
import sys
import re
import tempfile as _tempfile
import logging as _logging
import datetime as _datetime
import time as _time

python_version = sys.version_info[0:3]
version_string = ".".join([str(x) for x in python_version])
current_root = os.path.abspath(".")
python3x = python_version >= (3, 0)
python2x = python_version < (3, 0)
nix_based = os.name == "posix"
win_based = os.name == "nt"
temp_directory = _tempfile.gettempdir()

logger = _logging.getLogger(__name__)
if python_version >= (2, 7):
    #Surpresses warning that no logger is found if a parent logger is not set
    logger.addHandler(_logging.NullHandler())

# http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx

reg_exps = {
    "path": {
        "windows": {
            "valid": re.compile(r'^(?:[a-zA-Z]:\\|\\\\?|\\\\\?\\|\\\\\.\\)\
?(?:(?!(CLOCK\$(\\|$)|(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]| )\
(?:\..*|(\\|$))|.*\.$))(?:(?:(?![><:/"\\\|\?\*])[\x20-\u10FFFF])+\\?))*$'),
            "safe": re.compile(r'^([a-zA-Z]:\\)?[\w\d _\-\\\(\)]+$'),
            "filename": re.compile(r'^((?![><:/"\\\|\?\*])[ -~])+$')
        },
        "linux": {
            "valid": re.compile(r'^/?([\x01-\xFF]+/?)*$'),
            "safe": re.compile(r'^[\w\d\. _\-/\(\)]+$'),
            "filename": re.compile(r'^((?![><:/"\\\|\?\*])[ -~])+$')
        },
        "mac": {
            "valid": re.compile(r'^/?([\x01-\xFF]+/?)*$'),
            "safe": re.compile(r'^[\w\d\. _\-/\(\)]+$'),
            "filename": re.compile(r'^((?![><:/"\\\|\?\*])[ -~])+$')
        }
    },
    "python": {
        "module": {
            "attributes": re.compile(r'__([a-z]+)__ *= *[\'"](.+)[\'"]'),
            "imports": re.compile(r'^ *\t*(?:import|from)[ ]+(?:(\w+)[, ]*)+'),
            "functions": re.compile(r'^ *\t*def +(\w+)\('),
            "classes": re.compile(r'^ *\t*class +(\w+)\('),
            "docstrings": re.compile(r'^ *\t*"""(.*)"""|\'\'\'(.*)\'\'\'')
        }
    },
    "pii": {
        "phone_number": {
            "us": re.compile(r'((?:\(? ?\d{3} ?\)?[\. \-]?)?\d{3}[\. \-]?\d{4})')
        }
    },
    "datetime": {
        "format": {
            "%I": re.compile(r"\{(?:12)?\-?hours?\}"),
            "%H": re.compile(r"\{24\-?hours?\}"),
            "%S": re.compile(r"\{seco?n?d?s?\}"),
            "%M": re.compile(r"\{minu?t?e?s?\}"),
            "%f": re.compile(r"\{micro\-?(?:second)?s?\}"),
            "%Z": re.compile(r"\{(?:(tz|time\-?zone))?\}"),
            "%y": re.compile(r"\{years?\}"),
            "%Y": re.compile(r"\{years?\-?(?:(full|name|full\-?name))?s?\}"),
            "%m": re.compile(r"\{months?\}"),
            "%b": re.compile(r"\{months?\-?name\}"),
            "%B": re.compile(r"\{months?\-?(?:(full|full\-?name))?s?\}"),
            "%d": re.compile(r"\{days?\}"),
            "%w": re.compile(r"\{week\-?days?\}"),
            "%j": re.compile(r"\{year\-?days?\}"),
            "%a": re.compile(r"\{(?:week)?\-?days?\-?name\}"),
            "%A": re.compile(r"\{(?:week)?\-?days?\-?fullname\}"),
            "%U": re.compile(r"\{weeks?\}"),
            "%W": re.compile(r"\{mon(?:day)?\-?weeks?\}"),
            "%x": re.compile(r"\{date\}"),
            "%X": re.compile(r"\{time\}"),
            "%c": re.compile(r"\{date\-?time\}"),
            "%z": re.compile(r"\{(?:utc)?\-?offset\}"),
            "%p": re.compile(r"\{periods?\}"),
            "%Y-%m-%dT%H:%M:%S": re.compile(r"\{iso-?(?:format)?\}")
        },
        "date": re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]?[\d]{2})"),
        "time": re.compile(r"([\d]{2}:[\d]{2}(?:\.[\d]{6})?)"),
        "datetime": re.compile(r"((?:[\d]{2}|[\d]{4})[\- _\\/]?[\d]{2}[\- _\\/]?[\d]{2}T[\d]{2}:[\d]{2}(?:\.[\d]{6})?)")
    }
}

common_exts = {
    "pictures": (".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tif", ".tiff",
                 ".ico", ".mng", ".tga", ".psd", ".xcf", ".svg", ".icns"),
    "video": (".mkv", ".avi", ".mp4", ".mov", ".flv", ".mpeg", ".mpg", ".3gp",
              ".m4v", ".ogv", ".asf", ".m1v", ".m2v", ".mpe", ".ogv", ".wmv",
              ".rm", ".qt"),
    "music": (".mp3", ".ogg", ".wav", ".flac", ".aif", ".aiff", ".au", ".m4a",
              ".wma", ".mp2", ".m4a", ".m4p", ".aac", ".ra", ".mid", ".midi",
              ".mus", ".psf"),
    "documents": (".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx",
                  ".csv", ".epub", ".gdoc", ".odt", ".rtf", ".txt", ".info",
                  ".xps", ".gslides", ".gsheet"),
    "archives": (".zip", ".rar", ".7z", ".tar.gz", ".tgz", ".gz", ".bzip",
                 ".bzip2", ".bz2", ".xz", ".lzma", ".bin", ".tar"),
    "cd_images": (".iso", ".nrg", ".img", ".mds", ".mdf", ".cue", ".daa")
}

common_variables = {
    "hashes": {
        "empty_file": {
            "md5": "d41d8cd98f00b204e9800998ecf8427e",
            "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b\
7852b855"
        },
    },
}


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
        return "<Namespace: {0}...>".format(str(self.to_dict())[0:32])

    def __str__(self):
        return str(self.to_dict())

    @classmethod
    def from_dict(cls, dictionary):
        if not isinstance(dictionary, dict):
            raise TypeError("Must be a dictionary")
        return cls(**dictionary)

    def to_dict(self, in_dict=None):
        in_dict = in_dict if in_dict else self.__dict__
        out_dict = dict()
        for k, v in in_dict.items():
            if isinstance(v, Namespace):
                v = self.to_dict(v)
            out_dict[k] = v
        return out_dict

    def tree_view(self, sep="    "):
        base = self.to_dict()
        return tree_view(base, sep=sep)


def tree_view(dictionary, level=0, sep="|  "):
    """
    View a dictionary as a tree.
    """
    return "".join(["{0}{1}\n{2}".format(sep * level, k, tree_view(v, level + 1, sep=sep) if isinstance(v, dict)
           else "") for k, v in dictionary.items()])


def os_tree(directory):
    """
    Return a directories contents as a dictionary hierarchy.
    """
    if not os.path.exists(directory):
        raise OSError("Directory does not exist")
    if not os.path.isdir(directory):
        raise OSError("Path is not a directory")

    full_list = []
    for root, dirs, files in os.walk(directory):
        full_list.extend([os.path.join(root, d).lstrip(directory) + os.sep for d in dirs])
    tree = {os.path.basename(directory): {}}
    if not full_list:
        return {}
    for item in full_list:
        separated = item.split(os.sep)
        is_dir = separated[-1:] == ['']
        if is_dir:
            separated = separated[:-1]
        parent = tree[os.path.basename(directory)]
        for index, path in enumerate(separated):
            if path in parent:
                parent = parent[path]
                continue
            else:
                parent[path] = dict()
            parent = parent[path]
    return tree


# Some may ask why make everything into namespaces, I ask why not
regex = Namespace(**reg_exps)
exts = Namespace(**common_exts)
variables = Namespace(**common_variables)


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
        import ConfigParser
    except ImportError:
        import configparser as ConfigParser

    cfg_parser = ConfigParser.ConfigParser(**cfg_options)

    cfg_files = []

    if config_file:
        if not isinstance(config_file, (list, tuple)):
            if isinstance(config_file, str):
                cfg_files.append(config_file)
            else:
                raise TypeError("config_files must be a list or a string")
        else:
            cfg_files.extend(config_file)

    if auto_find:
        cfg_files.extend(find_all_files(current_root,
                                        ext=(".cfg", ".config", ".ini")))

    logger.info("config files to be used: {0}".format(cfg_files))

    if verify:
        cfg_parser.read([cfg for cfg in cfg_files if os.path.exists(cfg)])
    else:
        cfg_parser.read(cfg_files)

    return dict((section, dict(cfg_parser.items(section)))
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
    return sorted(unordered_list, key=lambda y: y[key])


def check_filename(filename):
    """
    Returns a boolean stating if the filename is safe to use or not. Note that
    this does not test for "legal" names accepted, but a more restricted set of:
    Letters, numbers, spaces, hyphens, underscores and periods
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    if regex.path.linux.filename.search(filename):
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
    if regex.path.linux.filename.search(filename):
        return filename
    safe_name = ""
    for char in filename:
        safe_name += char if regex.path.linux.filename.search(char) \
            else replacement
    return safe_name


def safe_path(path, replacement="_"):
    """
    Replace unsafe path characters with underscores.

    Supports windows and *nix systems.
    """
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    if os.sep not in path:
        return safe_filename(path, replacement=replacement)
    filename = safe_filename(os.path.basename(path))
    dirname = os.path.dirname(path)
    safe_dirname = ""
    regexp = regex.path.windows.safe if win_based else regex.path.linux.safe
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


def file_hash(path, hash_type="md5", block_size=65536):
    """
    Hash a given file with sha256 and return the hex digest.

    This function is designed to be non memory intensive.
    """
    import hashlib

    hashes = {"md5": hashlib.md5,
              "sha1": hashlib.sha1,
              "sha224": hashlib.sha224,
              "sha256": hashlib.sha256,
              "sha384": hashlib.sha384,
              "sha512": hashlib.sha512}
    if hash_type not in hashes:
        raise ValueError("Invalid hash type \"{0}\"".format(hash_type))
    hashed = hashes[hash_type]()
    with open(path, "rb") as infile:
        buf = infile.read(block_size)
        while len(buf) > 0:
            hashed.update(buf)
            buf = infile.read(block_size)
    return hashed.hexdigest()


def find_all_files_generator(directory=".", ext=None, name=None):
    """
    Walk through a file directory and return an iterator of files
    that match requirements.
    """
    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if ext:
                for end in ext:
                    if file_name.lower().endswith(end):
                        break
                else:
                    continue
            if name:
                if name.lower() not in file_name.lower():
                    continue
            yield join_paths(root, file_name, strict=True)


def find_all_files(directory=".", ext=None, name=None):
    """
    Returns a list of all files in a sub directory that match an extension
    and or part of a filename.
    """
    return list(find_all_files_generator(directory, ext=ext, name=name))


def remove_empty_directories(root_directory, dnd=False, ignore_errors=True):
    """
    Remove all empty folders from a path. Returns list of empty directories.
    """
    directory_list = []
    for root, directories, files in os.walk(root_directory, topdown=False):
        if (not directories and not files and os.path.exists(root) and
                root != root_directory and os.path.isdir(root)):
            directory_list.append(root)
            if not dnd:
                try:
                    os.rmdir(root)
                except OSError as err:
                    if ignore_errors:
                        logger.info("{0} could not be deleted".format(root))
                    else:
                        raise err
        elif directories and not files:
            for directory in directories:
                directory = join_paths(root, directory, strict=True)
                if (os.path.exists(directory) and os.path.isdir(directory) and
                        not os.listdir(directory)):
                    directory_list.append(directory)
                    if not dnd:
                        try:
                            os.rmdir(directory)
                        except OSError as err:
                            if ignore_errors:
                                logger.info("{0} could not be deleted".format(
                                    directory))
                            else:
                                raise err
    return directory_list


def remove_empty_files(root_directory, dnd=False, ignore_errors=True):
    """
    Remove all empty files from a path. Returns list of the empty files removed.
    """
    file_list = []
    for root, directories, files in os.walk(root_directory):
        for file_name in files:
            file_path = join_paths(root, file_name, strict=True)
            if os.path.isfile(file_path) and not os.path.getsize(file_path):
                if file_hash(file_path) == variables.hashes.empty_file.md5:
                    file_list.append(file_path)

    file_list = sorted(set(file_list))

    if not dnd:
        for afile in file_list:
            try:
                os.unlink(afile)
            except OSError as err:
                if ignore_errors:
                    logger.info("File {0} could not be deleted".format(afile))
                else:
                    raise err

    return file_list


def extract_all(archive_file, path=".", dnd=True):
    """
    Automatically detect archive type and extract all files to specified path.
    """
    import zipfile
    import tarfile

    if not os.path.exists(archive_file) or not os.path.getsize(archive_file):
        logger.error("File {0} unextractable".format(archive_file))
        raise OSError("File does not exist or has zero size")

    if zipfile.is_zipfile(archive_file):
        logger.debug("File {0} detected as a zip file".format(archive_file))
        archive = zipfile.ZipFile(archive_file)
    elif tarfile.is_tarfile(archive_file):
        logger.debug("File {0} detected as a tar file".format(archive_file))
        archive = tarfile.open(archive_file)
    else:
        raise TypeError("File is not a zip or tar archive")

    logger.debug("Extracting files to {0}".format(path))

    try:
        archive.extractall(path=path)
    finally:
        archive.close()

    if not dnd:
        logger.debug("Archive {0} will now be deleted".format(archive_file))
        os.unlink(archive_file)


class DateTime(_datetime.datetime):

    def __new__(cls, year=None, month=None, day=None, hour=0, minute=0,
                second=0, microsecond=0, tzinfo=None):
        #Taken from datetime.datetime.now()
        if year is not None:
            return super(DateTime, cls).__new__(cls, year, month, day, hour,
                                                minute, second, microsecond,
                                                tzinfo)
        if tzinfo is not None and not isinstance(tzinfo,
                                                 _datetime.datetime.tzinfo):
            raise TypeError("tzinfo argument must be None or a tzinfo subclass")
        converter = _time.localtime if tzinfo is None else _time.gmtime
        t = _time.time()
        t, frac = divmod(t, 1.0)
        us = int(frac * 1e6)
        tz = None
        if us == 1000000:
            t += 1
            us = 0
        y, m, d, hh, mm, ss, weekday, jday, dst = converter(t)
        ss = min(ss, 59)
        return super(DateTime, cls).__new__(cls, y, m, d, hh, mm, ss, us, tz)

    def __init__(self, *args):
        self.__dict__ = dict(
            year=self.year, month=self.month, day=self.day, hour=self.hour,
            minute=self.minute, second=self.second,
            microsecond=self.microsecond, timezone=self.tzinfo)

    def format(self, desired_format, *args, **kwargs):
        for strf, exp in regex.datetime.format.items():
            desired_format = exp.sub(strf, desired_format)
        return self.strftime(desired_format.format(*args, **kwargs))

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield (k, v)

    @classmethod
    def from_iso(cls, datetime):
        try:
            assert regex.datetime.datetime.match(datetime).groups()[0]
        except (ValueError, AssertionError, IndexError, AttributeError):
            raise TypeError("String is not in ISO format")
        try:
            return cls.strptime(datetime, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            return cls.strptime(datetime, "%Y-%m-%dT%H:%M:%S")

    #TODO add a 'from datetime'


def main(command_line_options=""):
    import argparse

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