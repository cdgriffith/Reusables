#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2019 - Chris Griffith - MIT License
from contextlib import contextmanager

__all__ = ['ignored']


@contextmanager
def ignored(*exceptions):
    """ Ignores provided exceptions with a context manager. """
    try:
        yield
    except exceptions:
        pass
