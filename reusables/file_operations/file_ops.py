#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
import os
import hashlib
import glob
import logging
from collections import defaultdict

from ..shared_variables import *


logger = logging.getLogger('reusables')

__all__ = ['os_tree', 'check_filename', 'count_files',
           'directory_duplicates', 'dup_finder', 'file_hash', 'find_files',
           'find_files_list', 'join_here', 'join_paths',
           'remove_empty_directories', 'remove_empty_files',
           'safe_filename', 'safe_path', 'touch']


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
               abspath=False, enable_scandir=False):
    """
    Walk through a file directory and return an iterator of files
    that match requirements. Will autodetect if name has glob as magic
    characters.

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
    :return: generator of all files in the specified directory
    """
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
            yield os.path.join(root, file_name)


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

    for item in find_files(directory, **kwargs):
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





