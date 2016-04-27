#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2016 - Chris Griffith - MIT License
"""
Improved dictionary management. Inspired by
javascript style referencing, as it's one of the few things they got right.
"""


class Namespace(dict):
    """
    Namespace container.
    Allows access to attributes by either class dot notation or item reference

    All valid:
        - namespace.spam.eggs
        - namespace['spam']['eggs']
        - namespace['spam'].eggs
    """

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs = args[0]
        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = Namespace(v)
            setattr(self, k, v)

    def __contains__(self, item):
        try:
            return dict.__contains__(self, item) or hasattr(self, item)
        except Exception:
            return False

    def __getattr__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return self[item]
            except KeyError:
                raise AttributeError(item)

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = Namespace(**value)
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            try:
                self[key] = value
            except Exception:
                raise AttributeError(key)
        else:
            object.__setattr__(self, key, value)

    def __delattr__(self, item):
        try:
            object.__getattribute__(self, item)
        except AttributeError:
            try:
                del self[item]
            except KeyError:
                raise AttributeError(item)
        else:
            object.__delattr__(self, item)

    def __repr__(self):
        return "<Namespace: {0}...>".format(str(self.to_dict())[0:32])

    def __str__(self):
        return str(self.to_dict())

    @classmethod
    def from_dict(cls, dictionary):
        if not isinstance(dictionary, dict):
            raise TypeError("Must be a dictionary")
        return cls(dictionary)

    def to_dict(self, in_dict=None):
        """
        Turn the Namespace and sub Namespaces back into a native
        python dictionary.

        :param in_dict: Do not use, for self recursion
        :return: python dictionary of this Namespace
        """
        in_dict = in_dict if in_dict else self
        out_dict = dict()
        for k, v in in_dict.items():
            if isinstance(v, Namespace):
                v = v.to_dict()
            out_dict[k] = v
        return out_dict

    def tree_view(self, sep="    "):
        base = self.to_dict()
        return tree_view(base, sep=sep)


def tree_view(dictionary, level=0, sep="|  "):
    """
    View a dictionary as a tree.
    """
    return "".join(["{0}{1}\n{2}".format(sep * level, k,
                   tree_view(v, level + 1, sep=sep) if isinstance(v, dict)
                   else "") for k, v in dictionary.items()])


