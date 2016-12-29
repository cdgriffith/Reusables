#!/usr/bin/env python
# -*- coding: UTF-8 -*-

_roman_dict = {'I': 1, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10, 'XL': 40, 'L': 50,
               'XC': 90, 'C': 100, 'CD': 400, 'D': 500, 'CM': 900, 'M': 1000}


_numbers = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
            6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
            15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
            19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty",
            50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty",
            90: "ninety"}

groups = {1: "", 2: "thousand", 3: "million", 4: "billion", 5: "trillion",
          6: "quadrillion", 7: "quintillion", 8: "sextillion", 9: "septillion",
          10: "octillion", 11: "nonillion", 12: "decillion"}


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


def int_to_words(number, european=False):
    """
    Converts an integer or float to words.

    :param The string, integer, or float to convert to words. The decimal
        can only be up to three places long, and max number allowed is 999
        decillion.
    :param european: If the string uses the european style formatting, i.e.
        decimal points instead of commas and commas instead of decimal points,
        set this paramater to True
    :return: The translated string
    """
    def ones(n):
        if n != 0:
            return _numbers[n]
        else:
            return ""

    def tens(n):
        teen = int("{}{}".format(n[0], n[1]))

        if n[0] == 0:
            return ones(n[1])
        for k, v in _numbers.items():
            if teen == k:
                return v
        else:
            ten = _numbers[int("{}0".format(n[0]))]
            one = _numbers[n[1]]
            return "{}-{}".format(ten, one)

    def hundreds(n):
        if n[0] == 0:
            return tens(n[1:])
        else:
            t = tens(n[1:])
            if t:
                return "{} hundred {}".format(_numbers[n[0]], tens(n[1:]))
            else:
                return "{} hundred".format(_numbers[n[0]])

    decimal = ''
    number = str(number)
    
    if european is False:
        if "." in number:
            decimal = number.split(".")[1]
        number = number.split(".")[0].replace(",", "")

    else:
        if "," in number:
            decimal = number.split(",")[1]
        number = number.split(",")[0].replace(".", "")

    if not number.isnumeric():
        raise ValueError("Number is not numeric")

    if int(number) == 0:
        return "zero"

    r = len(number) % 3
    number = number.replace(",", "").zfill(len(number) + 3 - r if r else 0)
    string = []

    d = [int(x) for x in decimal]
    n = [int(x) for x in number]

    group_set = int(len(n) / 3)
    index = 0
    while group_set != 0:
        if groups[group_set]:
            string.append("{} {}".format(hundreds(n[index:index+3]), groups[group_set]))
        else:
            value = hundreds(n[index:index+3])
            if value:
                string.append(value)

        group_set -= 1
        index += 3

    if decimal and int(decimal) != 0:
        if len(d) == 1:
            string.append("and {} tenths".format(ones(d[0])))
        elif len(d) == 2:
            string.append("and {} hundredths".format(tens(d)))
        elif len(d) == 3:
            string.append("and {} thousandths".format(hundreds(d)))
        else:
            raise Exception("Can't do decimals that long!")

    if len(string) > 1:
        if len(string) == 2 and string[-1].startswith("and"):
            return " ".join(string)
        else:
            return ", ".join(string)

    else:
        return string[0]
