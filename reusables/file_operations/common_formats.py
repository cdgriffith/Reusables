#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
import csv
import json

from ..shared_variables import *

__all__ = ['load_json', 'list_to_csv', 'save_json', 'csv_to_list']


def list_to_csv(my_list, csv_file):
    """
    Save a matrix (list of lists) to a file as a CSV

    .. code:: python

        my_list = [["Name", "Location"],
                   ["Chris", "South Pole"],
                   ["Harry", "Depth of Winter"],
                   ["Bob", "Skull"]]

        reusables.list_to_csv(my_list, "example.csv")

    example.csv

    .. code:: csv

        "Name","Location"
        "Chris","South Pole"
        "Harry","Depth of Winter"
        "Bob","Skull"

    :param my_list: list of lists to save to CSV
    :param csv_file: File to save data to
    """
    if PY3:
        csv_handler = open(csv_file, 'w', newline='')
    else:
        csv_handler = open(csv_file, 'wb')

    try:
        writer = csv.writer(csv_handler, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerows(my_list)
    finally:
        csv_handler.close()


def csv_to_list(csv_file):
    """
    Open and transform a CSV file into a matrix (list of lists).

    .. code:: python

        reusables.csv_to_list("example.csv")
        # [['Name', 'Location'],
        #  ['Chris', 'South Pole'],
        #  ['Harry', 'Depth of Winter'],
        #  ['Bob', 'Skull']]

    :param csv_file: Path to CSV file as str
    :return: list
    """
    with open(csv_file, 'r' if PY3 else 'rb') as f:
        return list(csv.reader(f))


def load_json(json_file, **kwargs):
    """
    Open and load data from a JSON file

    .. code:: python

        reusables.load_json("example.json")
        # {u'key_1': u'val_1', u'key_for_dict': {u'sub_dict_key': 8}}

    :param json_file: Path to JSON file as string
    :param kwargs: Additional arguments for the json.load command
    :return: Dictionary
    """
    with open(json_file) as f:
        return json.load(f, **kwargs)


def save_json(data, json_file, indent=4, **kwargs):
    """
    Takes a dictionary and saves it to a file as JSON

    .. code:: python

        my_dict = {"key_1": "val_1",
                   "key_for_dict": {"sub_dict_key": 8}}

        reusables.save_json(my_dict,"example.json")

    example.json

    .. code::

        {
            "key_1": "val_1",
            "key_for_dict": {
                "sub_dict_key": 8
            }
        }

    :param data: dictionary to save as JSON
    :param json_file: Path to save file location as str
    :param indent: Format the JSON file with so many numbers of spaces
    :param kwargs: Additional arguments for the json.dump command
    """
    with open(json_file, "w") as f:
        json.dump(data, f, indent=indent, **kwargs)
