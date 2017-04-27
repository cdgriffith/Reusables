#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License


def cut(string, characters=2, trailing="normal"):
    """
    Split a string into a list of N characters each.

    .. code:: python

        reusables.cut("abcdefghi")
        # ['ab', 'cd', 'ef', 'gh', 'i']

    trailing gives you the following options:

    * normal: leaves remaining characters in their own last position
    * remove: return the list without the remainder characters
    * combine: add the remainder characters to the previous set
    * error: raise an IndexError if there are remaining characters

    .. code:: python

        reusables.cut("abcdefghi", 2, "error")
        # Traceback (most recent call last):
        #     ...
        # IndexError: String of length 9 not divisible by 2 to splice

        reusables.cut("abcdefghi", 2, "remove")
        # ['ab', 'cd', 'ef', 'gh']

        reusables.cut("abcdefghi", 2, "combine")
        # ['ab', 'cd', 'ef', 'ghi']

    :param string: string to modify
    :param characters: how many characters to split it into
    :param trailing: "normal", "remove", "combine", or "error"
    :return: list of the cut string
    """
    split_str = [string[i:i + characters] for
                 i in range(0, len(string), characters)]

    if trailing != "normal" and len(split_str[-1]) != characters:
        if trailing.lower() == "remove":
            return split_str[:-1]
        if trailing.lower() == "combine" and len(split_str) >= 2:
            return split_str[:-2] + [split_str[-2] + split_str[-1]]
        if trailing.lower() == "error":
            raise IndexError("String of length {0} not divisible by {1} to"
                             " cut".format(len(string), characters))
    return split_str


