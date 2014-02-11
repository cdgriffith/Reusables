#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
holder for upcoming features that are not well written or tested.
"""

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