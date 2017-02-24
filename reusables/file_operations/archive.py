#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
import os
import zipfile
import tarfile
import logging

from .file_ops import find_files

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
                for nf in find_files(file_path, abspath=False, depth=depth):
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
