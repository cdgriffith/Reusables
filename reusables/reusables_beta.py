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


def reuse(func):
    """
    Save the variables entered into the function for reuse next time.

    Not: This is a dirty function that probably shouldn't be used.
    So when you do use it make sure to have fun with it!
    """
    # Could use DefaultDict but eh, it's another import
    _reuse_cache = dict()
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache = _reuse_cache.get(func.__name__, dict(args=[], kwargs={}))
        args = list(args)
        local_kwargs = cache['kwargs'].copy()
        if kwargs.get("reuse_view_cache"):
            del kwargs["reuse_view_cache"]
            return cache.copy()
        if kwargs.get("reuse_del_kwargs"):
            for x in kwargs["reuse_del_kwargs"]:
                if x in local_kwargs['kwargs']:
                    del local_kwargs['kwargs'][x]
            del kwargs["reuse_del_kwargs"]
        if kwargs.get("reuse_rep_args"):
            for old, new in kwargs["reuse_rep_args"]:
                if old in cache['args']:
                    tmp_args = list(cache['args'])
                    tmp_args[tmp_args.index(old)] = new
                    cache['args'] = tuple(tmp_args)
            del kwargs["reuse_rep_args"]
        if kwargs.get("reuse_reset"):
            cache.update(dict(args=[], kwargs={}))
            del kwargs["reuse_reset"]
        try:
            args.extend(cache['args'][len(args):])
        except IndexError:
            pass
        local_kwargs.update(kwargs)
        result = func(*tuple(args), **local_kwargs)
        _reuse_cache[func.__name__] = dict(args=tuple(args),
                                           kwargs=local_kwargs)
        return result
    return wrapper
