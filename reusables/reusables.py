#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Reusables - Commonly Consumed Code Commodities
#
# Copyright (c) 2014-2016 - Chris Griffith - MIT License

import os as _os
import sys as _sys
import re as _re
import tempfile as _tempfile
import csv as _csv
import json as _json
import subprocess as _subprocess

from .namespace import Namespace, ConfigNamespace
from .log import get_logger


python_version = _sys.version_info[0:3]
version_string = ".".join([str(x) for x in python_version])
current_root = _os.path.abspath(".")
python3x = PY3 = python_version >= (3, 0)
python2x = PY2 = python_version < (3, 0)
nix_based = _os.name == "posix"
win_based = _os.name == "nt"
temp_directory = _tempfile.gettempdir()
home = _os.path.abspath(_os.path.expanduser("~"))

logger = get_logger("reusables", level=10, stream=_sys.stdout, file_path=None)

# http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx

reg_exps = {
    "path": {
        "windows": {
            "valid": _re.compile(r'^(?:[a-zA-Z]:\\|\\\\?|\\\\\?\\|\\\\\.\\)?'
                r'(?:(?!(CLOCK\$(\\|$)|(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]| )'
                r'(?:\..*|(\\|$))|.*\.$))'
                r'(?:(?:(?![><:/"\\\|\?\*])[\x20-\u10FFFF])+\\?))*$'),
            "safe": _re.compile(r'^([a-zA-Z]:\\)?[\w\d _\-\\\(\)]+$'),
            "filename": _re.compile(r'^((?![><:/"\\\|\?\*])[ -~])+$')
        },
        "linux": {
            "valid": _re.compile(r'^/?([\x01-\xFF]+/?)*$'),
            "safe": _re.compile(r'^[\w\d\. _\-/\(\)]+$'),
            "filename": _re.compile(r'^((?![><:/"\\\|\?\*])[ -~])+$')
        },
        "mac": {
            "valid": _re.compile(r'^/?([\x01-\xFF]+/?)*$'),
            "safe": _re.compile(r'^[\w\d\. _\-/\(\)]+$'),
            "filename": _re.compile(r'^((?![><:/"\\\|\?\*])[ -~])+$')
        }
    },
    "python": {
        "module": {
            "attributes": _re.compile(r'__([a-z]+)__ *= *[\'"](.+)[\'"]'),
            "imports": _re.compile(r'^ *\t*(?:import|from)[ ]+(?:(\w+)[, ]*)+'),
            "functions": _re.compile(r'^ *\t*def +(\w+)\('),
            "classes": _re.compile(r'^ *\t*class +(\w+)\('),
            "docstrings": _re.compile(r'^ *\t*"""(.*)"""|\'\'\'(.*)\'\'\'')
        }
    },
    "pii": {
        "phone_number": {
            "us": _re.compile(r'((?:\(? ?\d{3} ?\)?[\. \-]?)?\d{3}'
                             r'[\. \-]?\d{4})')
        }
    },
}

common_exts = {
    "pictures": (".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tif", ".tiff",
                 ".ico", ".mng", ".tga", ".psd", ".xcf", ".svg", ".icns"),
    "video": (".mkv", ".avi", ".mp4", ".mov", ".flv", ".mpeg", ".mpg", ".3gp",
              ".m4v", ".ogv", ".asf", ".m1v", ".m2v", ".mpe", ".ogv", ".wmv",
              ".rm", ".qt", ".3g2", ".asf", ".vob"),
    "music": (".mp3", ".ogg", ".wav", ".flac", ".aif", ".aiff", ".au", ".m4a",
              ".wma", ".mp2", ".m4a", ".m4p", ".aac", ".ra", ".mid", ".midi",
              ".mus", ".psf"),
    "documents": (".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx",
                  ".csv", ".epub", ".gdoc", ".odt", ".rtf", ".txt", ".info",
                  ".xps", ".gslides", ".gsheet", ".pages", ".msg", ".tex",
                  ".wpd", ".wps", ".csv"),
    "archives": (".zip", ".rar", ".7z", ".tar.gz", ".tgz", ".gz", ".bzip",
                 ".bzip2", ".bz2", ".xz", ".lzma", ".bin", ".tar"),
    "cd_images": (".iso", ".nrg", ".img", ".mds", ".mdf", ".cue", ".daa"),
    "scripts": (".py", ".sh", ".bat"),
    "binaries": (".msi", ".exe"),
    "markup": (".html", ".htm", ".xml", ".yaml", ".json", ".raml", ".xhtml",
               ".kml"),

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

# Some may ask why make everything into namespaces, I ask why not
regex = Namespace(reg_exps)
exts = Namespace(common_exts)
variables = Namespace(common_variables)


def os_tree(directory):
    """
    Return a directories contents as a dictionary hierarchy.

    :param directory: path to directory to created the tree of.
    :return: dictionary of the directory
    """
    if not _os.path.exists(directory):
        raise OSError("Directory does not exist")
    if not _os.path.isdir(directory):
        raise OSError("Path is not a directory")

    full_list = []
    for root, dirs, files in _os.walk(directory):
        full_list.extend([_os.path.join(root, d).lstrip(directory) + _os.sep
                          for d in dirs])
    tree = {_os.path.basename(directory): {}}
    if not full_list:
        return {}
    for item in full_list:
        separated = item.split(_os.sep)
        is_dir = separated[-1:] == ['']
        if is_dir:
            separated = separated[:-1]
        parent = tree[_os.path.basename(directory)]
        for index, path in enumerate(separated):
            if path in parent:
                parent = parent[path]
                continue
            else:
                parent[path] = dict()
            parent = parent[path]
    return tree


def join_paths(*paths, **kwargs):
    """
    Join multiple paths together and return the absolute path of them. If 'safe'
    is specified, this function will 'clean' the path with the 'safe_path'
    function.

    Would like to do 'safe=False' instead of '**kwargs' but stupider versions
    of python *cough 2.6* don't like that after '*paths'.

    :param paths: paths to join together
    :param kwargs: 'safe', make them into a safe path it True
    :return: path as string
    """
    path = _os.path.abspath(paths[0])

    for next_path in paths[1:]:
        path = _os.path.join(path, next_path.lstrip(_os.sep).strip())
    path.rstrip(_os.sep)
    return path if not kwargs.get('safe') else safe_path(path)


def join_root(*paths, **kwargs):
    """
    Join any path or paths as a sub directory of the current file's directory.

    :param paths: paths to join together
    :param kwargs: 'strict', make them into a safe path unless set True
    :return: path as string
    """
    path = _os.path.abspath(".")
    for next_path in paths:
        next_path = next_path.lstrip(_os.sep).strip() if not \
            kwargs.get('strict') else next_path
        path = _os.path.abspath(_os.path.join(path, next_path))
    return path if kwargs.get('strict') else safe_path(path)


def config_dict(config_file=None, auto_find=False, verify=True, **cfg_options):
    """
    Return configuration options as dictionary. Accepts either a single
    config file or a list of files. Auto find will search for all .cfg, .config
    and .ini in the execution directory and package root (unsafe but handy).

    :param config_file: path or paths to the files location
    :param auto_find: look for a config type file at this location or below
    :param verify: make sure the file exists before trying to read
    :param cfg_options: options to pass to the parser
    :return: dictionary of the config files
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
        cfg_parser.read([cfg for cfg in cfg_files if _os.path.exists(cfg)])
    else:
        cfg_parser.read(cfg_files)

    return dict((section, dict(cfg_parser.items(section)))
                for section in cfg_parser.sections())


def config_namespace(config_file=None, auto_find=False,
                     verify=True, **cfg_options):
    """
    Return configuration options as a Namespace.

    :param config_file: path or paths to the files location
    :param auto_find: look for a config type file at this location or below
    :param verify: make sure the file exists before trying to read
    :param cfg_options: options to pass to the parser
    :return: Namespace of the config files
    """
    return ConfigNamespace(**config_dict(config_file, auto_find,
                                         verify, **cfg_options))


def sort_by(unordered_list, key, **sort_args):
    """
    Sort a list of dicts, tuples or lists by the provided dict key, or list/
    tuple position.

    :param unordered_list: list to sort
    :param key: key to sort on from the list
    :param sort_args: additional options to pass to sort, like 'reverse'
    :return: sorted list
    """
    return sorted(unordered_list, key=lambda y: y[key], **sort_args)


def check_filename(filename):
    """
    Returns a boolean stating if the filename is safe to use or not. Note that
    this does not test for "legal" names accepted, but a more restricted set of:
    Letters, numbers, spaces, hyphens, underscores and periods.

    :param filename: name of a file as a string
    :return: boolean if it is a safe file name
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
    Letters, numbers, spaces, hyphens, underscores and periods.

    :param filename: name of a file as a string
    :param replacement: character to use as a replacement of bad characters
    :return: safe filename string
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
    Replace unsafe path characters with underscores. Do NOT use this
    with existing paths that cannot be modified, this to to help generate
    new, clean paths.

    Supports windows and *nix systems.

    :param path: path as a string
    :param replacement: character to use in place of bad characters
    :return: a safer path
    """
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    if _os.sep not in path:
        return safe_filename(path, replacement=replacement)
    filename = safe_filename(_os.path.basename(path))
    dirname = _os.path.dirname(path)
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
    sanitized_path = _os.path.normpath("{path}{sep}{filename}".format(
        path=safe_dirname,
        sep=_os.sep if not safe_dirname.endswith(_os.sep) else "",
        filename=filename))
    if (not filename and
            path.endswith(_os.sep) and
            not sanitized_path.endswith(_os.sep)):
        sanitized_path += _os.sep
    return sanitized_path


def file_hash(path, hash_type="md5", block_size=65536):
    """
    Hash a given file with sha256 and return the hex digest.

    This function is designed to be non memory intensive.

    :param path: location of the file to hash
    :param hash_type: string name of the hash to use
    :param block_size: amount of bytes to add to hasher at a time
    :return: file's hash
    """
    import hashlib
    if (python_version >= (2, 7) and
            hash_type not in hashlib.algorithms_available):
        raise ValueError("Invalid hash type \"{0}\"".format(hash_type))
    elif hash_type not in ("md5", "sha1", "sha224",
                           "sha256", "sha384", "sha512"):
        raise ValueError("Invalid hash type \"{0}\"".format(hash_type))
    hashed = hashlib.new(hash_type)
    with open(path, "rb") as infile:
        buf = infile.read(block_size)
        while len(buf) > 0:
            hashed.update(buf)
            buf = infile.read(block_size)
    return hashed.hexdigest()


def count_all_files(directory=".", ext=None, name=None):
    """
    Perform the same operation as 'find_all_files' but return an integer count
    instead of a list.

    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :type directory: str
    :type ext: str
    :type name: str
    :return: count of files matching requirements as integer
    """

    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    count = 0
    for root, dirs, files in _os.walk(directory):
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
            count += 1
    return count


def find_all_files_generator(directory=".", ext=None, name=None):
    """
    Walk through a file directory and return an iterator of files
    that match requirements.

    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :type directory: str
    :type ext: str | tuple | list
    :type name: str
    :return: generator of all files in the specified directory
    """
    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    for root, dirs, files in _os.walk(directory):
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

    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :type directory: str
    :type ext: str
    :type name: str
    :return: list of all files in the specified directory
    """
    return list(find_all_files_generator(directory, ext=ext, name=name))


def remove_empty_directories(root_directory, dry_run=False, ignore_errors=True):
    """
    Remove all empty folders from a path. Returns list of empty directories.

    :param root_directory: base directory to start at
    :param dry_run: just return a list of what would be removed
    :param ignore_errors: Permissions are a pain, just ignore if you blocked
    :type root_directory: str
    :type dry_run: bool
    :type ignore_errors: bool
    :return: list of removed directories
    """
    directory_list = []
    for root, directories, files in _os.walk(root_directory, topdown=False):
        if (not directories and not files and _os.path.exists(root) and
                root != root_directory and _os.path.isdir(root)):
            directory_list.append(root)
            if not dry_run:
                try:
                    _os.rmdir(root)
                except OSError as err:
                    if ignore_errors:
                        logger.info("{0} could not be deleted".format(root))
                    else:
                        raise err
        elif directories and not files:
            for directory in directories:
                directory = join_paths(root, directory, strict=True)
                if (_os.path.exists(directory) and _os.path.isdir(directory) and
                        not _os.listdir(directory)):
                    directory_list.append(directory)
                    if not dry_run:
                        try:
                            _os.rmdir(directory)
                        except OSError as err:
                            if ignore_errors:
                                logger.info("{0} could not be deleted".format(
                                    directory))
                            else:
                                raise err
    return directory_list


def remove_empty_files(root_directory, dry_run=False, ignore_errors=True):
    """
    Remove all empty files from a path. Returns list of the empty files removed.

    :param root_directory: base directory to start at
    :param dry_run: just return a list of what would be removed
    :param ignore_errors: Permissions are a pain, just ignore if you blocked
    :type root_directory: str
    :type dry_run: bool
    :type ignore_errors: bool
    :return: list of removed files
    """
    file_list = []
    for root, directories, files in _os.walk(root_directory):
        for file_name in files:
            file_path = join_paths(root, file_name, strict=True)
            if _os.path.isfile(file_path) and not _os.path.getsize(file_path):
                if file_hash(file_path) == variables.hashes.empty_file.md5:
                    file_list.append(file_path)

    file_list = sorted(set(file_list))

    if not dry_run:
        for afile in file_list:
            try:
                _os.unlink(afile)
            except OSError as err:
                if ignore_errors:
                    logger.info("File {0} could not be deleted".format(afile))
                else:
                    raise err

    return file_list


def extract_all(archive_file, path=".", delete_on_success=False,
                enable_rar=False):
    """
    Automatically detect archive type and extract all files to specified path.

    :param archive_file: path to file to extract
    :param path: location to extract to
    :param delete_on_success: Will delete the original archive if set to True
    :param enable_rar: include the rarfile import and extract
    """
    import zipfile
    import tarfile

    if not _os.path.exists(archive_file) or not _os.path.getsize(archive_file):
        logger.error("File {0} unextractable".format(archive_file))
        raise OSError("File does not exist or has zero size")

    archive = None
    if zipfile.is_zipfile(archive_file):
        logger.debug("File {0} detected as a zip file".format(archive_file))
        archive = zipfile.ZipFile(archive_file)
    elif tarfile.is_tarfile(archive_file):
        logger.debug("File {0} detected as a tar file".format(archive_file))
        archive = tarfile.open(archive_file)
    elif enable_rar:
        import rarfile
        if rarfile.is_rarfile(archive_file):
            logger.debug("File {0} detected as a rar file".format(archive_file))
            archive = rarfile.RarFile(archive_file)

    if not archive:
        raise TypeError("File is not a known archive")

    logger.debug("Extracting files to {0}".format(path))

    try:
        archive.extractall(path=path)
    finally:
        archive.close()

    if delete_on_success:
        logger.debug("Archive {0} will now be deleted".format(archive_file))
        _os.unlink(archive_file)


def dup_finder_generator(file_path, directory="."):
    """
    Check a directory for duplicates of the specified file. It's designed to
    be as fast as possible by doing lighter checks before progressing to
    more extensive ones, in order they are:

    1. File size
    2. First twenty bytes
    3. Full SHA256 compare

    :param file_path: Path to file to check for duplicates of
    :param directory: Directory to dig recurivly into to look for duplicates
    :return: generators
    """
    size = _os.path.getsize(file_path)
    if size == 0:
        for x in remove_empty_files(directory, dry_run=True):
            yield x
    with open(file_path, 'rb') as f:
        first_twenty = f.read(20)
    file_sha256 = file_hash(file_path, "sha256")

    for root, directories, files in _os.walk(directory):
        for each_file in files:
            test_file = _os.path.join(root, each_file)
            if _os.path.getsize(test_file) == size:
                try:
                    with open(test_file, 'rb') as f:
                        test_first_twenty = f.read(20)
                except OSError:
                    logger.warning("Could not open file to compare - "
                                   "{}".format(test_file))
                else:
                    if first_twenty == test_first_twenty:
                        if file_hash(test_file, "sha256") == file_sha256:
                            yield test_file


def list_to_csv(my_list, csv_file):
    """
    Save a matrix (list of lists) to a file as a CSV

    :param my_list: list of lists to save to CSV
    :param csv_file: File to save data to
    """
    if PY3:
        csv_handler = open(csv_file, 'w', newline='')
    else:
        csv_handler = open(csv_file, 'wb')

    try:
        writer = _csv.writer(csv_handler, delimiter=',', quoting=_csv.QUOTE_ALL)
        writer.writerows(my_list)
    finally:
        csv_handler.close()


def csv_to_list(csv_file):
    """
    Open and transform a CSV file into a matrix (list of lists),


    :param csv_file: Path to CSV file as str
    :return: list
    """
    with open(csv_file, 'r' if PY3 else 'rb') as f:
        return list(_csv.reader(f))


def load_json(json_file, **kwargs):
    """
    Open and load data from a JSON file

    :param json_file: Path to JSON file as string
    :param kwargs: Additional arguments for the json.load command
    :return: Dictionary
    """
    with open(json_file) as f:
        return _json.load(f, **kwargs)


def save_json(data, json_file, indent=4, **kwargs):
    """
    Takes a dictionary and saves it to a file as JSON

    :param data: dictionary to save as JSON
    :param json_file: Path to save file location as str
    :param indent: Format the JSON file with so many numbers of spaces
    :param kwargs: Additional arguments for the json.dump command
    """
    with open(json_file, "w") as f:
        _json.dump(data, f, indent=indent, **kwargs)


def touch(path):
    """
    Native 'touch' functionality in python

    :param path: path to file to 'touch'
    """
    with open(path, 'a'):
        _os.utime(path, None)


def run(command, input=None, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE,
        timeout=None, **kwargs):
    """
    Cross platform compatible subprocess with CompletedProcess return.

    :param command: command to run, str if shell=True otherwise must be list
    :param input: send something `communicate`
    :param stdout: PIPE or None
    :param stderr: PIPE or None
    :param timeout: max time to wait for command to complete
    :param kwargs: additional arguments to pass to Popen
    :return: CompletedProcess class
    """
    if _sys.version_info >= (3, 5):
        return _subprocess.run(command, input=input, stdout=stdout,
                               stderr=stderr, timeout=timeout, **kwargs)

    class CompletedProcess(object):
        """A backwards compatible clone of subprocess.CompletedProcess"""

        def __init__(self, args, returncode, stdout=None, stderr=None):
            self.args = args
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

        def __repr__(self):
            args = ['args={0!r}'.format(self.args),
                    'returncode={0!r}'.format(self.returncode),
                    'stdout={0!r}'.format(self.stdout) if self.stdout else '',
                    'stderr={0!r}'.format(self.stderr) if self.stderr else '']
            return "{0}({1})".format(type(self).__name__,
                                     ', '.join(filter(None, args)))

        def check_returncode(self):
            if self.returncode:
                raise _subprocess.CalledProcessError(self.returncode,
                                                     self.args,
                                                     self.stdout,
                                                     self.stderr)

    proc = _subprocess.Popen(command, stdout=stdout, stderr=stderr, **kwargs)
    if PY3:
        out, err = proc.communicate(input=input, timeout=timeout)
    else:
        if timeout:
            raise NotImplementedError("Timeout is only available on python 3")
        out, err = proc.communicate(input=input)
    return CompletedProcess(command, proc.returncode, out, err)
