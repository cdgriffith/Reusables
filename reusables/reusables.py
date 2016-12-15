#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Reusables - Commonly Consumed Code Commodities
#
# Copyright (c) 2014-2016 - Chris Griffith - MIT License

import os as _os
import sys as _sys
import csv as _csv
import json as _json
import subprocess as _subprocess
import glob as _glob
import hashlib as _hashlib
import zipfile as _zipfile
import tarfile as _tarfile
try:
    import ConfigParser as _ConfigParser
except ImportError:
    import configparser as _ConfigParser

from .namespace import ConfigNamespace
from .log import get_logger
from .dt import DateTime
from .shared_variables import *

_logger = get_logger("reusables", level=10, stream=None, file_path=None)


def os_tree(directory):
    """
    Return a directories contents as a dictionary hierarchy.

    .. code:: python

        reusables.os_tree(".")
        # {'doc': {'build': {'doctrees': {},
        #                   'html': {'_sources': {}, '_static': {}}},
        #         'source': {}},
        #  'reusables': {'__pycache__': {}},
        #  'test': {'__pycache__': {}, 'data': {}}}


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
    function. This will clean root decelerations from the path
    after the first item.

    Would like to do 'safe=False' instead of '**kwargs' but stupider versions
    of python *cough 2.6* don't like that after '*paths'.

    .. code: python

        reusables.join_paths("var", "\\log", "/test")
        'C:\\Users\\Me\\var\\log\\test'

        os.path.join("var", "\\log", "/test")
        '/test'

    :param paths: paths to join together
    :param kwargs: 'safe', make them into a safe path it True
    :return: abspath as string
    """
    path = _os.path.abspath(paths[0])

    for next_path in paths[1:]:
        path = _os.path.join(path, next_path.lstrip("\\").lstrip("/").strip())
    path.rstrip(_os.sep)
    return path if not kwargs.get('safe') else safe_path(path)


def join_here(*paths, **kwargs):
    """
    Join any path or paths as a sub directory of the current file's directory.

    .. code:: python

        reusables.join_here("Makefile")
        # 'C:\\Reusables\\Makefile'

    :param paths: paths to join together
    :param kwargs: 'strict', do not strip os.sep
    :param kwargs: 'safe', make them into a safe path it True
    :return: abspath as string
    """
    path = _os.path.abspath(".")
    for next_path in paths:
        next_path = next_path.lstrip("\\").lstrip("/").strip() if not \
            kwargs.get('strict') else next_path
        path = _os.path.abspath(_os.path.join(path, next_path))
    return path if not kwargs.get('safe') else safe_path(path)


def config_dict(config_file=None, auto_find=False, verify=True, **cfg_options):
    """
    Return configuration options as dictionary. Accepts either a single
    config file or a list of files. Auto find will search for all .cfg, .config
    and .ini in the execution directory and package root (unsafe but handy).

    .. code:: python

        reusables.config_dict(os.path.join("test", "data", "test_config.ini"))
        # {'General': {'example': 'A regular string'},
        #  'Section 2': {'anint': '234',
        #                'examplelist': '234,123,234,543',
        #                'floatly': '4.4',
        #                'my_bool': 'yes'}}


    :param config_file: path or paths to the files location
    :param auto_find: look for a config type file at this location or below
    :param verify: make sure the file exists before trying to read
    :param cfg_options: options to pass to the parser
    :return: dictionary of the config files
    """
    if not config_file:
        config_file = []

    cfg_parser = _ConfigParser.ConfigParser(**cfg_options)
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
        cfg_files.extend(find_all_files(
            current_root if isinstance(auto_find, bool) else auto_find,
            ext=(".cfg", ".config", ".ini")))

    _logger.info("config files to be used: {0}".format(cfg_files))

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

    .. code:: python

        reusables.config_namespace(os.path.join("test", "data",
                                                "test_config.ini"))
        # <Namespace: {'General': {'example': 'A regul...>


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

    .. code:: python

        my_list = [{"a": 5, "d": 2}, {"a": 1, "b": 2}]

        reusables.sort_by(my_list, "a")
        # [{'a': 1, 'b': 2}, {'a': 5, 'd': 2}]


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
    Hash a given file with md5, or any other and return the hex digest. You
    can run `hashlib.algorithms_available` to see which are available on your
    system unless you have an archaic python version, you poor soul).

    This function is designed to be non memory intensive.

    .. code:: python

        reusables.file_hash(test_structure.zip")
        # '61e387de305201a2c915a4f4277d6663'

    :param path: location of the file to hash
    :param hash_type: string name of the hash to use
    :param block_size: amount of bytes to add to hasher at a time
    :return: file's hash
    """
    if (python_version >= (2, 7) and
            hash_type not in _hashlib.algorithms_available):
        raise ValueError("Invalid hash type \"{0}\"".format(hash_type))
    elif hash_type not in ("md5", "sha1", "sha224",
                           "sha256", "sha384", "sha512"):
        raise ValueError("Invalid hash type \"{0}\"".format(hash_type))
    hashed = _hashlib.new(hash_type)
    with open(path, "rb") as infile:
        buf = infile.read(block_size)
        while len(buf) > 0:
            hashed.update(buf)
            buf = infile.read(block_size)
    return hashed.hexdigest()


def count_all_files(directory=".", ext=None, name=None,
                    match_case=False, disable_glob=False, depth=None):
    """
    Perform the same operation as 'find_all_files' but return an integer count
    instead of a list.

    .. code:: python

        reusables.count_all_files(name="ex", match_case=True))
        # 2

    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :param match_case: If name has to be a direct match or not
    :param disable_glob: Do not look for globable names or use glob magic check
    :param depth: How many directories down to search
    :return: count of files matching requirements as integer
    """

    return sum(1 for _ in find_all_files_generator(directory, ext, name,
                                                   match_case, disable_glob,
                                                   depth))


def find_all_files_generator(directory=".", ext=None, name=None,
                             match_case=False, disable_glob=False, depth=None,
                             abspath=False):
    """
    Walk through a file directory and return an iterator of files
    that match requirements. Will autodetect if name has glob as magic
    characters.

    .. code:: python

        list(reusables.find_all_files_generator(name="ex", match_case=True))
        # ['C:\\example.pdf',
        #  'C:\\My_exam_score.txt']

        list(reusables.find_all_files_generator(name="*free*"))
        # ['C:\\my_stuff\\Freedom_fight.pdf']

    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :param match_case: If name or ext has to be a direct match or not
    :param disable_glob: Do not look for globable names or use glob magic check
    :param depth: How many directories down to search
    :param abspath: Return files with their absolute paths
    :return: generator of all files in the specified directory
    """
    if ext or not name:
        disable_glob = True
    if not disable_glob:
        disable_glob = not _glob.has_magic(name)

    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    if abspath:
        directory = _os.path.abspath(directory)
    starting_depth = directory.count(_os.sep)

    for root, dirs, files in _os.walk(directory):
        if depth and root.count(_os.sep) - starting_depth >= depth:
            continue

        if not disable_glob:
            if match_case:
                raise ValueError("Cannot use glob and match case, please "
                                 "either disable glob or not set match_case")
            glob_generator = _glob.iglob(_os.path.join(root, name))
            for item in glob_generator:
                yield item
            continue

        for file_name in files:
            if ext:
                for end in ext:
                    if file_name.lower().endswith(end.lower() if not
                                                  match_case else end):
                        break
                else:
                    continue
            if name:
                if match_case and name not in file_name:
                    continue
                elif name.lower() not in file_name.lower():
                    continue
            yield _os.path.join(root, file_name)


def find_all_files(directory=".", ext=None, name=None, match_case=False,
                   disable_glob=False, depth=None, abspath=False):
    """
    Returns a list of all files in a sub directory that match an extension
    and or part of a filename. Will autodetect if name has glob as magic
    characters.

    .. code:: python

        reusables.find_all_files(ext=".pdf")
        # ['C:\\Example.pdf',
        #  'C:\\how_to_program.pdf',
        #  'C:\\Hunks_and_Chicks.pdf']

        reusables.find_all_files(name="*chris*")
        # ['C:\\Christmas_card.docx',
        #  'C:\\chris_stuff.zip']


    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :param match_case: If name has to be a direct match or not
    :param disable_glob: Do not look for globable names or use glob magic check
    :param depth: How many directories down to search
    :param abspath: Return files with their absolute paths
    :return: list of all files in the specified directory
    """
    return list(find_all_files_generator(directory, ext=ext, name=name,
                                         match_case=match_case,
                                         disable_glob=disable_glob,
                                         depth=depth, abspath=abspath))


def remove_empty_directories(root_directory, dry_run=False, ignore_errors=True):
    """
    Remove all empty folders from a path. Returns list of empty directories.

    :param root_directory: base directory to start at
    :param dry_run: just return a list of what would be removed
    :param ignore_errors: Permissions are a pain, just ignore if you blocked
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
                        _logger.info("{0} could not be deleted".format(root))
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
                                _logger.info("{0} could not be deleted".format(
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
                    _logger.info("File {0} could not be deleted".format(afile))
                else:
                    raise err

    return file_list


def extract_all(archive_file, path=".", delete_on_success=False,
                enable_rar=False):
    """
    Automatically detect archive type and extract all files to specified path.

    .. code:: python

        import os

        os.listdir(".")
        # ['test_structure.zip']

        reusables.extract_all("test_structure.zip")

        os.listdir(".")
        # [ 'test_structure', 'test_structure.zip']


    :param archive_file: path to file to extract
    :param path: location to extract to
    :param delete_on_success: Will delete the original archive if set to True
    :param enable_rar: include the rarfile import and extract
    :return: path to extracted files
    """

    if not _os.path.exists(archive_file) or not _os.path.getsize(archive_file):
        _logger.error("File {0} unextractable".format(archive_file))
        raise OSError("File does not exist or has zero size")

    archive = None
    if _zipfile.is_zipfile(archive_file):
        _logger.debug("File {0} detected as a zip file".format(archive_file))
        archive = _zipfile.ZipFile(archive_file)
    elif _tarfile.is_tarfile(archive_file):
        _logger.debug("File {0} detected as a tar file".format(archive_file))
        archive = _tarfile.open(archive_file)
    elif enable_rar:
        import rarfile
        if rarfile.is_rarfile(archive_file):
            _logger.debug("File {0} detected as "
                          "a rar file".format(archive_file))
            archive = rarfile.RarFile(archive_file)

    if not archive:
        raise TypeError("File is not a known archive")

    _logger.debug("Extracting files to {0}".format(path))

    try:
        archive.extractall(path=path)
    finally:
        archive.close()

    if delete_on_success:
        _logger.debug("Archive {0} will now be deleted".format(archive_file))
        _os.unlink(archive_file)

    return _os.path.abspath(path)


def archive_all(files_to_archive, name="archive", archive_type="zip",
                overwrite=False, store=False, depth=None, err_non_exist=True,
                allow_zip_64=True, **tarfile_kwargs):
    """ Archive a list of files (or files inside a folder), can chose between

        - zip
        - tar
        - gz (tar.gz, tgz)
        - bz2 (tar.bz2)

    .. code:: python

        reusables.archive_all(['reusables', '.travis.yml'],
                              name="my_archive", archive_type="bz2")
        # 'C:\\Users\\Me\\Reusables\\my_archive.bz2'

    :param files_to_archive: list of files and folders to archive
    :param name: path and name of archive file (no extension)
    :param archive_type: supported archive, automatically appended to name
    :param overwrite: overwrite if archive exists
    :param store: zipfile only, True will not compress files
    :param depth: specify max depth for folders
    :param err_non_exist: raise error if provided file does not exist
    :param allow_zip_64: must be enabled for zip files larger than 2GB
    :param tarfile_kwargs: extra args to pass to tarfile.open
    :return: path to created archive
    """
    if not isinstance(files_to_archive, (list, tuple)):
        files_to_archive = [files_to_archive]

    archive_type = archive_type.lower()
    filename = "{0}.{1}".format(name, archive_type)

    if not overwrite and _os.path.exists(filename):
        raise OSError("File exists and overwrite not specified")

    if archive_type == "zip":
        archive = _zipfile.ZipFile(filename, 'w',
                                   _zipfile.ZIP_STORED if store else
                                   _zipfile.ZIP_DEFLATED,
                                   allowZip64=allow_zip_64)
        write = archive.write
    elif archive_type in ("tar.gz", "tgz", "gz", "tar.bz2", "bz2", "tar"):
        if archive_type == "tar":
            archive = _tarfile.open(filename, 'w:', **tarfile_kwargs)
        elif archive_type in ("tgz", "tar.gz", "gz"):
            archive = _tarfile.open(filename, 'w:gz', **tarfile_kwargs)
        elif archive_type in ("tar.gz2", "bz2"):
            archive = _tarfile.open(filename, 'w:bz2', **tarfile_kwargs)
        else:
            raise Exception("Should not be here")
        write = archive.add
    else:
        raise ValueError("archive_type must be zip, tar.gz, tgz, or gz")

    try:
        for file_path in files_to_archive:
            if _os.path.isfile(file_path):
                if err_non_exist and not _os.path.exists(file_path):
                    raise OSError("File {0} does not exist".format(file_path))
                write(file_path)
            elif _os.path.isdir(file_path):
                for nf in find_all_files_generator(file_path, abspath=False,
                                                   depth=depth):
                    write(nf)
    except (Exception, KeyboardInterrupt) as err:
        try:
            archive.close()
        finally:
            _os.unlink(filename)
        raise err
    else:
        archive.close()

    return _os.path.abspath(filename)


def dup_finder_generator(file_path, directory="."):
    """
    Check a directory for duplicates of the specified file. It's designed to
    be as fast as possible by doing lighter checks before progressing to
    more extensive ones, in order they are:

    1. File size
    2. First twenty bytes
    3. Full SHA256 compare

    .. code:: python

        list(reusables.dup_finder_generator(
             "test_structure\\files_2\\empty_file"))
        # ['C:\\Reusables\\test\\data\\fake_dir',
        #  'C:\\Reusables\\test\\data\\test_structure\\Files\\empty_file_1',
        #  'C:\\Reusables\\test\\data\\test_structure\\Files\\empty_file_2',
        #  'C:\\Reusables\\test\\data\\test_structure\\files_2\\empty_file']

    :param file_path: Path to file to check for duplicates of
    :param directory: Directory to dig recursively into to look for duplicates
    :return: generators
    """
    size = _os.path.getsize(file_path)
    if size == 0:
        for empty_file in remove_empty_files(directory, dry_run=True):
            yield empty_file
    else:
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
                        _logger.warning("Could not open file to compare - "
                                        "{0}".format(test_file))
                    else:
                        if first_twenty == test_first_twenty:
                            if file_hash(test_file, "sha256") == file_sha256:
                                yield _os.path.abspath(test_file)


def list_to_csv(my_list, csv_file):
    """
    Save a matrix (list of lists) to a file as a CSV

    .. code:: python

        my_list = [["Name", "Location"],
                   ["Chris", "South Pole"],
                   ["Harry", "Depth of Winter"],
                   ["Bob", "Skull"]]

        reusables.list_to_csv(my_list, "example.csv")

    example.csv

    .. code:: csv

        "Name","Location"
        "Chris","South Pole"
        "Harry","Depth of Winter"
        "Bob","Skull"

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
    Open and transform a CSV file into a matrix (list of lists).

    .. code:: python

        reusables.csv_to_list("example.csv")
        # [['Name', 'Location'],
        #  ['Chris', 'South Pole'],
        #  ['Harry', 'Depth of Winter'],
        #  ['Bob', 'Skull']]

    :param csv_file: Path to CSV file as str
    :return: list
    """
    with open(csv_file, 'r' if PY3 else 'rb') as f:
        return list(_csv.reader(f))


def load_json(json_file, **kwargs):
    """
    Open and load data from a JSON file

    .. code:: python

        reusables.load_json("example.json")
        # {u'key_1': u'val_1', u'key_for_dict': {u'sub_dict_key': 8}}

    :param json_file: Path to JSON file as string
    :param kwargs: Additional arguments for the json.load command
    :return: Dictionary
    """
    with open(json_file) as f:
        return _json.load(f, **kwargs)


def save_json(data, json_file, indent=4, **kwargs):
    """
    Takes a dictionary and saves it to a file as JSON

    .. code:: python

        my_dict = {"key_1": "val_1",
                   "key_for_dict": {"sub_dict_key": 8}}

        reusables.save_json(my_dict,"example.json")

    example.json

    .. code::

        {
            "key_1": "val_1",
            "key_for_dict": {
                "sub_dict_key": 8
            }
        }

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
        timeout=None, copy_local_env=False, **kwargs):
    """
    Cross platform compatible subprocess with CompletedProcess return.

    No formatting or encoding is performed on the output of subprocess, so it's
    output will appear the same on each version / interpreter as before.

    .. code:: python

        reusables.run('echo "hello world!', shell=True)
        # CPython 3.6
        # CompletedProcess(args='echo "hello world!', returncode=0,
        #                  stdout=b'"hello world!\\r\\n', stderr=b'')
        #
        # PyPy 5.4 (Python 2.7.10)
        # CompletedProcess(args='echo "hello world!', returncode=0L,
        # stdout='"hello world!\\r\\n')

    Timeout is only usable in Python 3.X, as it was not implemented before then,
    a NotImplementedError will be raised if specified on 2.x version of Python.

    :param command: command to run, str if shell=True otherwise must be list
    :param input: send something `communicate`
    :param stdout: PIPE or None
    :param stderr: PIPE or None
    :param timeout: max time to wait for command to complete
    :param copy_local_env: Use all current ENV vars in the subprocess as well
    :param kwargs: additional arguments to pass to Popen
    :return: CompletedProcess class
    """
    if copy_local_env:
        # Copy local env first and overwrite with anything manually specified
        env = _os.environ.copy()
        env.update(kwargs.get('env', {}))
    else:
        env = kwargs.get('env')

    if _sys.version_info >= (3, 5):
        return _subprocess.run(command, input=input, stdout=stdout,
                               stderr=stderr, timeout=timeout, env=env,
                               **kwargs)

    # Created here instead of root level as it should never need to be
    # manually created or referenced
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
                if python_version < (2, 7):
                    raise _subprocess.CalledProcessError(self.returncode,
                                                         self.args)
                raise _subprocess.CalledProcessError(self.returncode,
                                                     self.args,
                                                     self.stdout)

    proc = _subprocess.Popen(command, stdout=stdout, stderr=stderr,
                             env=env, **kwargs)
    if PY3:
        out, err = proc.communicate(input=input, timeout=timeout)
    else:
        if timeout:
            raise NotImplementedError("Timeout is only available on Python 3")
        out, err = proc.communicate(input=input)
    return CompletedProcess(command, proc.returncode, out, err)


def now(utc=False, tz=None):
    """
    Get a current DateTime object. By default is local.

    .. code:: python

        reusables.now()
        # DateTime(2016, 12, 8, 22, 5, 2, 517000)

        reusables.now().format("It's {24-hour}:{min}")
        # "It's 22:05"

    :param utc: bool, default False, UTC time not local
    :param tz: TimeZone as specified by the datetime module
    :return: reusables.DateTime
    """
    return DateTime.utcnow() if utc else DateTime.now(tz=tz)


def splice(string, characters=2, trailing="normal"):
    """
    Split a string into a list of N characters each.

    .. code:: python

        reusables.splice("abcdefghi")
        # ['ab', 'cd', 'ef', 'gh', 'i']

    trailing gives you the following options:

    * normal: leaves remaining characters in their own last position
    * remove: return the list without the remainder characters
    * combine: add the remainder characters to the previous set
    * error: raise an IndexError if there are remaining characters

    .. code:: python

        reusables.splice("abcdefghi", 2, "error")
        # Traceback (most recent call last):
        #     ...
        # IndexError: String of length 9 not divisible by 2 to splice

        reusables.splice("abcdefghi", 2, "remove")
        # ['ab', 'cd', 'ef', 'gh']

        reusables.splice("abcdefghi", 2, "combine")
        # ['ab', 'cd', 'ef', 'ghi']

    :param string: string to modify
    :param characters: how many characters to split it into
    :param trailing: "normal", "remove", "combine", or "error"
    :return: list of the spliced string
    """
    split_str = [string[i:i + characters] for
                 i in range(0, len(string), characters)]

    if trailing != "normal" and len(split_str[-1]) != characters:
        if trailing.lower() == "remove":
            return split_str[:-1]
        if trailing.lower() == "combine" and len(split_str) >= 2:
            return split_str[:-2] + [split_str[-2] + split_str[-1]]
        if trailing.lower() == "error":
            raise IndexError("String of length {0} not divisible by {1} to"
                             " splice".format(len(string), characters))
    return split_str


