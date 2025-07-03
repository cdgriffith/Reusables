#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2025 - Chris Griffith - MIT License
from contextlib import contextmanager

__all__ = ["ignored"]


@contextmanager
def ignored(*exceptions):
    """Ignores provided exceptions with a context manager."""
    try:
        yield
    except exceptions:
        pass


class Singleton(type):
    """Singleton design pattern metaclass. Ensures only one instance of an object exists at any time."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
