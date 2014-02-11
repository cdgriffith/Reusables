#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
holder for upcoming features that are not well written or tested.
"""

def hashfile(fi_loc, hash_type="md5", blocksize=65536):
    """
    Hash a given file with sha256 and return the hex digest.

    This function is designed to be non memory intensive.
    """
    import hashlib
    hashes = {"md5": hashlib.md5,
              "sha1": hashlib.sha1,
    }
    if hash_type not in hashes:
        raise ValueError("Hash type must be either: md5 or sha1")
    hasher = hashes[hash_type]()
    with open(fi_loc, "rb") as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.hexdigest()