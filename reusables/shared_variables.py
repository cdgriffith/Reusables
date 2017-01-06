#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
import re as _re
import os as _os
import sys as _sys
import tempfile as _tempfile

from .namespace import Namespace

python_version = _sys.version_info[0:3]
version_string = ".".join([str(x) for x in python_version])
current_root = _os.path.abspath(".")
python3x = PY3 = python_version >= (3, 0)
python2x = PY2 = python_version < (3, 0)
nix_based = _os.name == "posix"
win_based = _os.name == "nt"
temp_directory = _tempfile.gettempdir()
home = _os.path.abspath(_os.path.expanduser("~"))

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

sizes = Namespace.from_dict({
    "kb": 1024,
    "mb": 1024 * 1024,
    "gb": 1024 * 1024 * 1024,
    "tb": 1024 * 1024 * 1024 * 1024,
    "pb": 1024 * 1024 * 1024 * 1024 * 1024
})

# Some may ask why make everything into namespaces, I ask why not
regex = Namespace(reg_exps)
exts = Namespace(common_exts)
variables = Namespace(common_variables)

exts._protected_keys.extend(exts.keys())
