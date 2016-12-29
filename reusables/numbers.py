#!/usr/bin/env python
# -*- coding: UTF-8 -*-

_roman_dict = {'I': 1, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10, 'XL': 40, 'L': 50,
               'XC': 90, 'C': 100, 'CD': 400, 'D': 500, 'CM': 900, 'M': 1000}


def int_to_roman(integer):
    """
    Convert an integer into a string of roman numbers.

    :param integer:
    :return: roman string
    """
    if not isinstance(integer, int):
        raise ValueError("Input integer must be of type int")
    output = []
    while integer > 0:
        for r, i in sorted(_roman_dict.items(),
                           key=lambda x: x[1], reverse=True):
            while integer >= i:
                output.append(r)
                integer -= i
    return "".join(output)


def roman_to_int(roman_string):
    """
    Converts a string of roman numbers into an integer.

    :param roman_string: XVI or similar
    :return: parsed integer
    """
    roman_string = roman_string.upper().strip()
    if "IIII" in roman_string:
        raise ValueError("Malformed roman string")
    value = 0
    skip_one = False
    last_number = None
    for i, letter in enumerate(roman_string):
        if letter not in _roman_dict:
            raise ValueError("Malformed roman string")
        if skip_one:
            skip_one = False
            continue
        if i < (len(roman_string) - 1):
            double_check = letter + roman_string[i + 1]
            if double_check in _roman_dict:
                if last_number and _roman_dict[double_check] > last_number:
                    raise ValueError("Malformed roman string")
                last_number = _roman_dict[double_check]
                value += _roman_dict[double_check]
                skip_one = True
                continue
        if last_number and _roman_dict[letter] > last_number:
            raise ValueError("Malformed roman string")
        last_number = _roman_dict[letter]
        value += _roman_dict[letter]
    return value
