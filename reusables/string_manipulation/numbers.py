#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Part of the Reusables package.
#
# Copyright (c) 2014-2017 - Chris Griffith - MIT License
_roman_dict = {'I': 1, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10, 'XL': 40, 'L': 50,
               'XC': 90, 'C': 100, 'CD': 400, 'D': 500, 'CM': 900, 'M': 1000}


_numbers = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
            6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
            15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
            19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty",
            50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty",
            90: "ninety"}

_places = {1: "", 2: "thousand", 3: "million", 4: "billion", 5: "trillion",
           6: "quadrillion", 7: "quintillion", 8: "sextillion",
           9: "septillion", 10: "octillion", 11: "nonillion", 12: "decillion"}


def int_to_roman(integer):
    """
    Convert an integer into a string of roman numbers.

    .. code: python

        reusables.int_to_roman(445)
        # 'CDXLV'


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

    .. code: python

        reusables.roman_to_int("XXXVI")
        # 36


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


def int_to_words(number, european=False):
    """
    Converts an integer or float to words.

    .. code: python

        reusables.int_to_number(445)
        # 'four hundred forty-five'

        reusables.int_to_number(1.45)
        # 'one and forty-five hundredths'

    :param number: String, integer, or float to convert to words. The decimal
        can only be up to three places long, and max number allowed is 999
        decillion.
    :param european: If the string uses the european style formatting, i.e.
        decimal points instead of commas and commas instead of decimal points,
        set this parameter to True
    :return: The translated string
    """
    def ones(n):
        return "" if n == 0 else _numbers[n]

    def tens(n):
        teen = int("{0}{1}".format(n[0], n[1]))

        if n[0] == 0:
            return ones(n[1])
        if teen in _numbers:
            return _numbers[teen]
        else:
            ten = _numbers[int("{0}0".format(n[0]))]
            one = _numbers[n[1]]
            return "{0}-{1}".format(ten, one)

    def hundreds(n):
        if n[0] == 0:
            return tens(n[1:])
        else:
            t = tens(n[1:])
            return "{0} hundred {1}".format(_numbers[n[0]], "" if not t else t)

    def comma_separated(list_of_strings):
        if len(list_of_strings) > 1:
            return "{0} ".format("" if len(list_of_strings) == 2
                                 else ",").join(list_of_strings)
        else:
            return list_of_strings[0]

    def while_loop(list_of_numbers, final_list):
        index = 0
        group_set = int(len(list_of_numbers) / 3)
        while group_set != 0:
            value = hundreds(list_of_numbers[index:index + 3])
            if value:
                final_list.append("{0} {1}".format(value, _places[group_set])
                                  if _places[group_set] else value)
            group_set -= 1
            index += 3

    number_list = []
    decimal_list = []

    decimal = ''
    number = str(number)
    group_delimiter, point_delimiter = (",", ".") \
        if not european else (".", ",")

    if point_delimiter in number:
        decimal = number.split(point_delimiter)[1]
        number = number.split(point_delimiter)[0].replace(
            group_delimiter, "")
    elif group_delimiter in number:
        number = number.replace(group_delimiter, "")

    if not number.isdigit():
        raise ValueError("Number is not numeric")

    if decimal and not decimal.isdigit():
        raise ValueError("Decimal is not numeric")

    if int(number) == 0:
        number_list.append("zero")

    r = len(number) % 3
    d_r = len(decimal) % 3
    number = number.zfill(len(number) + 3 - r if r else 0)
    f_decimal = decimal.zfill(len(decimal) + 3 - d_r if d_r else 0)

    d = [int(x) for x in f_decimal]
    n = [int(x) for x in number]

    while_loop(n, number_list)

    if decimal and int(decimal) != 0:
        while_loop(d, decimal_list)

        if decimal_list:
            name = ''
            if len(decimal) % 3 == 1:
                name = 'ten'
            elif len(decimal) % 3 == 2:
                name = 'hundred'

            place = int((str(len(decimal) / 3).split(".")[0]))
            number_list.append("and {0} {1}{2}{3}ths".format(
                comma_separated(decimal_list), name,
                "-" if name and _places[place+1] else "", _places[place+1]))

    return comma_separated(number_list)
