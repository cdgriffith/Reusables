#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2019 - Chris Griffith - MIT License
import os
import zipfile
import tarfile
import logging
import csv
import json
import hashlib
import glob
import shutil
from collections import defaultdict
try:
    import ConfigParser as ConfigParser
except ImportError:
    import configparser as ConfigParser

from reusables.namespace import *
from reusables.shared_variables import *

__all__ = ['load_json', 'list_to_csv', 'save_json', 'csv_to_list',
           'extract', 'archive', 'config_dict', 'config_namespace',
           'os_tree', 'check_filename', 'count_files',
           'directory_duplicates', 'dup_finder', 'file_hash', 'find_files',
           'find_files_list', 'join_here', 'join_paths',
           'remove_empty_directories', 'remove_empty_files',
           'safe_filename', 'safe_path', 'touch', 'sync_dirs']

logger = logging.getLogger('reusables')


def extract(archive_file, path=".", delete_on_success=False,
            enable_rar=False):
    """
    Automatically detect archive type and extract all files to specified path.

    .. code:: python

        import os

        os.listdir(".")
        # ['test_structure.zip']

        reusables.extract("test_structure.zip")

        os.listdir(".")
        # [ 'test_structure', 'test_structure.zip']


    :param archive_file: path to file to extract
    :param path: location to extract to
    :param delete_on_success: Will delete the original archive if set to True
    :param enable_rar: include the rarfile import and extract
    :return: path to extracted files
    """

    if not os.path.exists(archive_file) or not os.path.getsize(archive_file):
        logger.error("File {0} unextractable".format(archive_file))
        raise OSError("File does not exist or has zero size")

    arch = None
    if zipfile.is_zipfile(archive_file):
        logger.debug("File {0} detected as a zip file".format(archive_file))
        arch = zipfile.ZipFile(archive_file)
    elif tarfile.is_tarfile(archive_file):
        logger.debug("File {0} detected as a tar file".format(archive_file))
        arch = tarfile.open(archive_file)
    elif enable_rar:
        import rarfile
        if rarfile.is_rarfile(archive_file):
            logger.debug("File {0} detected as "
                         "a rar file".format(archive_file))
            arch = rarfile.RarFile(archive_file)

    if not arch:
        raise TypeError("File is not a known archive")

    logger.debug("Extracting files to {0}".format(path))

    try:
        arch.extractall(path=path)
    finally:
        arch.close()

    if delete_on_success:
        logger.debug("Archive {0} will now be deleted".format(archive_file))
        os.unlink(archive_file)

    return os.path.abspath(path)


def archive(files_to_archive, name="archive.zip", archive_type=None,
            overwrite=False, store=False, depth=None, err_non_exist=True,
            allow_zip_64=True, **tarfile_kwargs):
    """ Archive a list of files (or files inside a folder), can chose between

        - zip
        - tar
        - gz (tar.gz, tgz)
        - bz2 (tar.bz2)

    .. code:: python

        reusables.archive(['reusables', '.travis.yml'],
                              name="my_archive.bz2")
        # 'C:\\Users\\Me\\Reusables\\my_archive.bz2'

    :param files_to_archive: list of files and folders to archive
    :param name: path and name of archive file
    :param archive_type: auto-detects unless specified
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

    if not archive_type:
        if name.lower().endswith("zip"):
            archive_type = "zip"
        elif name.lower().endswith("gz"):
            archive_type = "gz"
        elif name.lower().endswith("z2"):
            archive_type = "bz2"
        elif name.lower().endswith("tar"):
            archive_type = "tar"
        else:
            err_msg = ("Could not determine archive "
                       "type based off {0}".format(name))
            logger.error(err_msg)
            raise ValueError(err_msg)
        logger.debug("{0} file detected for {1}".format(archive_type, name))
    elif archive_type not in ("tar", "gz", "bz2", "zip"):
        err_msg = ("archive_type must be zip, gz, bz2,"
                   " or gz, was {0}".format(archive_type))
        logger.error(err_msg)
        raise ValueError(err_msg)

    if not overwrite and os.path.exists(name):
        err_msg = "File {0} exists and overwrite not specified".format(name)
        logger.error(err_msg)
        raise OSError(err_msg)

    if archive_type == "zip":
        arch = zipfile.ZipFile(name, 'w',
                               zipfile.ZIP_STORED if store else
                               zipfile.ZIP_DEFLATED,
                               allowZip64=allow_zip_64)
        write = arch.write
    elif archive_type in ("tar", "gz", "bz2"):
        mode = archive_type if archive_type != "tar" else ""
        arch = tarfile.open(name, 'w:{0}'.format(mode), **tarfile_kwargs)
        write = arch.add
    else:
        raise ValueError("archive_type must be zip, gz, bz2, or gz")

    try:
        for file_path in files_to_archive:
            if os.path.isfile(file_path):
                if err_non_exist and not os.path.exists(file_path):
                    raise OSError("File {0} does not exist".format(file_path))
                write(file_path)
            elif os.path.isdir(file_path):
                for nf in find_files(file_path, abspath=False,
                                     depth=depth, disable_pathlib=True):
                    write(nf)
    except (Exception, KeyboardInterrupt) as err:
        logger.exception("Could not archive {0}".format(files_to_archive))
        try:
            arch.close()
        finally:
            os.unlink(name)
        raise err
    else:
        arch.close()

    return os.path.abspath(name)


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
        writer = csv.writer(csv_handler, delimiter=',', quoting=csv.QUOTE_ALL)
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
        return list(csv.reader(f))


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
        return json.load(f, **kwargs)


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
        json.dump(data, f, indent=indent, **kwargs)


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
        cfg_files.extend(find_files_list(
            current_root if isinstance(auto_find, bool) else auto_find,
            ext=(".cfg", ".config", ".ini"), disable_pathlib=True))

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


def _walk(directory, enable_scandir=False, **kwargs):
    """
    Internal function to return walk generator either from os or scandir

    :param directory: directory to traverse
    :param enable_scandir: on python < 3.5 enable external scandir package
    :param kwargs: arguments to pass to walk function
    :return: walk generator
    """
    walk = os.walk
    if python_version < (3, 5) and enable_scandir:
        import scandir
        walk = scandir.walk
    return walk(directory, **kwargs)


def os_tree(directory, enable_scandir=False):
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
    :param enable_scandir: on python < 3.5 enable external scandir package
    :return: dictionary of the directory
    """
    if not os.path.exists(directory):
        raise OSError("Directory does not exist")
    if not os.path.isdir(directory):
        raise OSError("Path is not a directory")

    full_list = []
    for root, dirs, files in _walk(directory, enable_scandir=enable_scandir):
        full_list.extend([os.path.join(root, d).lstrip(directory) + os.sep
                          for d in dirs])
    tree = {os.path.basename(directory): {}}
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


def file_hash(path, hash_type="md5", block_size=65536, hex_digest=True):
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
    :param hex_digest: returned as hexdigest, false will return digest
    :return: file's hash
    """
    hashed = hashlib.new(hash_type)
    with open(path, "rb") as infile:
        buf = infile.read(block_size)
        while len(buf) > 0:
            hashed.update(buf)
            buf = infile.read(block_size)
    return hashed.hexdigest() if hex_digest else hashed.digest()


def find_files_list(*args, **kwargs):
    """ Returns a list of find_files generator"""
    return list(find_files(*args, **kwargs))


def count_files(*args, **kwargs):
    """ Returns an integer of all files found using find_files"""
    return sum(1 for _ in find_files(*args, **kwargs))


def find_files(directory=".", ext=None, name=None,
               match_case=False, disable_glob=False, depth=None,
               abspath=False, enable_scandir=False, disable_pathlib=False):
    """
    Walk through a file directory and return an iterator of files
    that match requirements. Will autodetect if name has glob as magic
    characters.

    Returns pathlib objects by default with Python versions 3.4 or grater
    unless disable_pathlib is enabled.

    Note: For the example below, you can use find_files_list to return as a
    list, this is simply an easy way to show the output.

    .. code:: python

        list(reusables.find_files(name="ex", match_case=True))
        # ['C:\\example.pdf',
        #  'C:\\My_exam_score.txt']

        list(reusables.find_files(name="*free*"))
        # ['C:\\my_stuff\\Freedom_fight.pdf']

        list(reusables.find_files(ext=".pdf"))
        # ['C:\\Example.pdf',
        #  'C:\\how_to_program.pdf',
        #  'C:\\Hunks_and_Chicks.pdf']

        list(reusables.find_files(name="*chris*"))
        # ['C:\\Christmas_card.docx',
        #  'C:\\chris_stuff.zip']

    :param directory: Top location to recursively search for matching files
    :param ext: Extensions of the file you are looking for
    :param name: Part of the file name
    :param match_case: If name or ext has to be a direct match or not
    :param disable_glob: Do not look for globable names or use glob magic check
    :param depth: How many directories down to search
    :param abspath: Return files with their absolute paths
    :param enable_scandir: on python < 3.5 enable external scandir package
    :param disable_pathlib: only return string, not path objects
    :return: generator of all files in the specified directory
    """
    def pathed(path):
        if python_version < (3, 4) or disable_pathlib:
            return path
        import pathlib
        return pathlib.Path(path)

    if ext or not name:
        disable_glob = True
    if not disable_glob:
        disable_glob = not glob.has_magic(name)

    if ext and isinstance(ext, str):
        ext = [ext]
    elif ext and not isinstance(ext, (list, tuple)):
        raise TypeError("extension must be either one extension or a list")
    if abspath:
        directory = os.path.abspath(directory)
    starting_depth = directory.count(os.sep)

    for root, dirs, files in _walk(directory, enable_scandir=enable_scandir):
        if depth and root.count(os.sep) - starting_depth >= depth:
            continue

        if not disable_glob:
            if match_case:
                raise ValueError("Cannot use glob and match case, please "
                                 "either disable glob or not set match_case")
            glob_generator = glob.iglob(os.path.join(root, name))
            for item in glob_generator:
                yield pathed(item)
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
            yield pathed(os.path.join(root, file_name))


def remove_empty_directories(root_directory, dry_run=False, ignore_errors=True,
                             enable_scandir=False):
    """
    Remove all empty folders from a path. Returns list of empty directories.

    :param root_directory: base directory to start at
    :param dry_run: just return a list of what would be removed
    :param ignore_errors: Permissions are a pain, just ignore if you blocked
    :param enable_scandir: on python < 3.5 enable external scandir package
    :return: list of removed directories
    """
    listdir = os.listdir
    if python_version < (3, 5) and enable_scandir:
        import scandir as _scandir

        def listdir(directory):
            return list(_scandir.scandir(directory))

    directory_list = []
    for root, directories, files in _walk(root_directory,
                                          enable_scandir=enable_scandir,
                                          topdown=False):
        if (not directories and not files and os.path.exists(root) and
                    root != root_directory and os.path.isdir(root)):
            directory_list.append(root)
            if not dry_run:
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
                        not listdir(directory)):
                    directory_list.append(directory)
                    if not dry_run:
                        try:
                            os.rmdir(directory)
                        except OSError as err:
                            if ignore_errors:
                                logger.info("{0} could not be deleted".format(
                                    directory))
                            else:
                                raise err
    return directory_list


def remove_empty_files(root_directory, dry_run=False, ignore_errors=True,
                       enable_scandir=False):
    """
    Remove all empty files from a path. Returns list of the empty files removed.

    :param root_directory: base directory to start at
    :param dry_run: just return a list of what would be removed
    :param ignore_errors: Permissions are a pain, just ignore if you blocked
    :param enable_scandir: on python < 3.5 enable external scandir package
    :return: list of removed files
    """
    file_list = []
    for root, directories, files in _walk(root_directory,
                                          enable_scandir=enable_scandir):
        for file_name in files:
            file_path = join_paths(root, file_name, strict=True)
            if os.path.isfile(file_path) and not os.path.getsize(file_path):
                if file_hash(file_path) == variables.hashes.empty_file.md5:
                    file_list.append(file_path)

    file_list = sorted(set(file_list))

    if not dry_run:
        for afile in file_list:
            try:
                os.unlink(afile)
            except OSError as err:
                if ignore_errors:
                    logger.info("File {0} could not be deleted".format(afile))
                else:
                    raise err

    return file_list


def dup_finder(file_path, directory=".", enable_scandir=False):
    """
    Check a directory for duplicates of the specified file. This is meant
    for a single file only, for checking a directory for dups, use
    directory_duplicates.

    This is designed to be as fast as possible by doing lighter checks
    before progressing to
    more extensive ones, in order they are:

    1. File size
    2. First twenty bytes
    3. Full SHA256 compare

    .. code:: python

        list(reusables.dup_finder(
             "test_structure\\files_2\\empty_file"))
        # ['C:\\Reusables\\test\\data\\fake_dir',
        #  'C:\\Reusables\\test\\data\\test_structure\\Files\\empty_file_1',
        #  'C:\\Reusables\\test\\data\\test_structure\\Files\\empty_file_2',
        #  'C:\\Reusables\\test\\data\\test_structure\\files_2\\empty_file']

    :param file_path: Path to file to check for duplicates of
    :param directory: Directory to dig recursively into to look for duplicates
    :param enable_scandir: on python < 3.5 enable external scandir package
    :return: generators
    """
    size = os.path.getsize(file_path)
    if size == 0:
        for empty_file in remove_empty_files(directory, dry_run=True):
            yield empty_file
    else:
        with open(file_path, 'rb') as f:
            first_twenty = f.read(20)
        file_sha256 = file_hash(file_path, "sha256")

        for root, directories, files in _walk(directory,
                                              enable_scandir=enable_scandir):
            for each_file in files:
                test_file = os.path.join(root, each_file)
                if os.path.getsize(test_file) == size:
                    try:
                        with open(test_file, 'rb') as f:
                            test_first_twenty = f.read(20)
                    except OSError:
                        logger.warning("Could not open file to compare - "
                                       "{0}".format(test_file))
                    else:
                        if first_twenty == test_first_twenty:
                            if file_hash(test_file, "sha256") == file_sha256:
                                yield os.path.abspath(test_file)


def directory_duplicates(directory, hash_type='md5', **kwargs):
    """
    Find all duplicates in a directory. Will return a list, in that list
    are lists of duplicate files.

    .. code: python

        dups = reusables.directory_duplicates('C:\\Users\\Me\\Pictures')

        print(len(dups))
        # 56
        print(dups)
        # [['C:\\Users\\Me\\Pictures\\IMG_20161127.jpg',
        # 'C:\\Users\\Me\\Pictures\\Phone\\IMG_20161127.jpg'], ...


    :param directory: Directory to search
    :param hash_type: Type of hash to perform
    :param kwargs: Arguments to pass to find_files to narrow file types
    :return: list of lists of dups"""
    size_map, hash_map = defaultdict(list), defaultdict(list)

    for item in find_files(directory, disable_pathlib=True, **kwargs):
        file_size = os.path.getsize(item)
        size_map[file_size].append(item)

    for possible_dups in (v for v in size_map.values() if len(v) > 1):
        for each_item in possible_dups:
            item_hash = file_hash(each_item, hash_type=hash_type)
            hash_map[item_hash].append(each_item)

    return [v for v in hash_map.values() if len(v) > 1]


def touch(path):
    """
    Native 'touch' functionality in python

    :param path: path to file to 'touch'
    """
    with open(path, 'a'):
        os.utime(path, None)


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
    path = os.path.abspath(paths[0])

    for next_path in paths[1:]:
        path = os.path.join(path, next_path.lstrip("\\").lstrip("/").strip())
    path.rstrip(os.sep)
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
    path = os.path.abspath(".")
    for next_path in paths:
        next_path = next_path.lstrip("\\").lstrip("/").strip() if not \
            kwargs.get('strict') else next_path
        path = os.path.abspath(os.path.join(path, next_path))
    return path if not kwargs.get('safe') else safe_path(path)


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


def sync_dirs(dir1, dir2, checksums=True, overwrite=False,
              only_log_errors=True):
    """
    Make sure all files in directory 1 exist in directory 2.

    :param dir1: Copy from
    :param dir2: Copy too
    :param checksums: Use hashes to make sure file contents match
    :param overwrite: If sizes don't match, overwrite with file from dir 1
    :param only_log_errors: Do not raise copy errors, only log them
    :return: None
    """
    def cp(f1, f2):
        try:
            shutil.copy(f1, f2)
        except OSError:
            if only_log_errors:
                logger.error("Could not copy {} to {}".format(f1, f2))
            else:
                raise

    for file in find_files(dir1, disable_pathlib=True):
        path_two = os.path.join(dir2, file[len(dir1)+1:])
        try:
            os.makedirs(os.path.dirname(path_two))
        except OSError:
            pass  # Because exists_ok doesn't exist in 2.x
        if os.path.exists(path_two):
            if os.path.getsize(file) != os.path.getsize(path_two):
                logger.info("File sizes do not match: "
                            "{} - {}".format(file, path_two))
                if overwrite:
                    logger.info("Overwriting {}".format(path_two))
                    cp(file, path_two)
            elif checksums and (file_hash(file) != file_hash(path_two)):
                logger.warning("Files do not match: "
                               "{} - {}".format(file, path_two))
                if overwrite:
                    logger.info("Overwriting {}".format(file, path_two))
                    cp(file, path_two)
        else:
            logger.info("Copying {} to {}".format(file, path_two))
            cp(file, path_two)








