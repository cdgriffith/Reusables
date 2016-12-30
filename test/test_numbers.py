import reusables

from .common_test_data import *

roman_list = [(1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV'), (5, 'V'), (6, 'VI'),
              (7, 'VII'), (8, 'VIII'), (9, 'IX'), (10, 'X'), (11, 'XI'),
              (12, 'XII'), (13, 'XIII'), (14, 'XIV'), (15, 'XV'), (16, 'XVI'),
              (17, 'XVII'), (18, 'XVIII'), (19, 'XIX'), (20, 'XX'), (21, 'XXI'),
              (22, 'XXII'), (23, 'XXIII'), (24, 'XXIV'), (25, 'XXV'),
              (26, 'XXVI'), (27, 'XXVII'), (28, 'XXVIII'), (29, 'XXIX'),
              (30, 'XXX'), (31, 'XXXI'), (32, 'XXXII'), (33, 'XXXIII'),
              (34, 'XXXIV'), (35, 'XXXV'), (36, 'XXXVI'), (37, 'XXXVII'),
              (38, 'XXXVIII'), (39, 'XXXIX'), (40, 'XL'), (41, 'XLI'),
              (42, 'XLII'), (43, 'XLIII'), (44, 'XLIV'), (45, 'XLV'),
              (46, 'XLVI'), (47, 'XLVII'), (48, 'XLVIII'), (49, 'XLIX'),
              (50, 'L'), (51, 'LI'), (52, 'LII'), (53, 'LIII'), (54, 'LIV'),
              (55, 'LV'), (56, 'LVI'), (57, 'LVII'), (58, 'LVIII'),
              (59, 'LIX'), (60, 'LX'), (61, 'LXI'), (62, 'LXII'), (63, 'LXIII'),
              (64, 'LXIV'), (65, 'LXV'), (66, 'LXVI'), (67, 'LXVII'),
              (68, 'LXVIII'), (69, 'LXIX'), (70, 'LXX'), (71, 'LXXI'),
              (72, 'LXXII'), (73, 'LXXIII'), (74, 'LXXIV'), (75, 'LXXV'),
              (76, 'LXXVI'), (77, 'LXXVII'), (78, 'LXXVIII'), (79, 'LXXIX'),
              (80, 'LXXX'), (81, 'LXXXI'), (82, 'LXXXII'), (83, 'LXXXIII'),
              (84, 'LXXXIV'), (85, 'LXXXV'), (86, 'LXXXVI'), (87, 'LXXXVII'),
              (88, 'LXXXVIII'), (89, 'LXXXIX'), (90, 'XC'), (91, 'XCI'),
              (92, 'XCII'), (93, 'XCIII'), (94, 'XCIV'), (95, 'XCV'),
              (96, 'XCVI'), (97, 'XCVII'), (98, 'XCVIII'), (99, 'XCIX'),
              (100, 'C'), (501, 'DI'), (530, 'DXXX'), (550, 'DL'),
              (707, 'DCCVII'), (890, 'DCCCXC'), (900, 'CM'), (1500, 'MD'),
              (1800, 'MDCCC')]

numbers_list = [(0, 'zero'), ('1,000.00', 'one thousand'),
                (1000.00, 'one thousand'),
                (18005607, 'eighteen million, five thousand, six hundred seven'),
                (13.13, 'thirteen and thirteen hundredths'),
                ('1', 'one'), ('1.0', 'one'),
                (89.1, 'eighty-nine and one tenths'),
                ('89.1', 'eighty-nine and one tenths'),
                ('1.00012', 'one and twelve hundred-thousandths'),
                (10.10, 'ten and one tenths'),
                (0.11111, 'zero and eleven thousand one hundred eleven '
                          'hundred-thousandths')]

european_numbers = [('123.456.789',
                     'one hundred twenty-three million, four hundred '
                     'fifty-six thousand, seven hundred eighty-nine'),
                    ('1,345', 'one and three hundred forty-five thousandths'),
                    ('10.000,5', 'ten thousand and five tenths')]


class TestNumbers(BaseTestClass):

    def test_roman_from_int(self):
        for line in roman_list:
            value = reusables.int_to_roman(int(line[0]))
            assert value == line[1], (line, value)

    def test_bad_roman(self):
        try:
            reusables.int_to_roman("5")
        except ValueError:
            pass
        else:
            raise AssertionError("Should only accept int")

        try:
            reusables.roman_to_int("IIIII")
        except ValueError:
            pass
        else:
            raise AssertionError("Parsed malformed roman string")

        try:
            reusables.roman_to_int("XXXXC")
        except ValueError:
            pass
        else:
            raise AssertionError("Parsed malformed roman string")

        try:
            reusables.roman_to_int("IVCD")
        except ValueError:
            pass
        else:
            raise AssertionError("Parsed malformed roman string")

        try:
            reusables.roman_to_int("Hello")
        except ValueError:
            pass
        else:
            raise AssertionError("Parsed malformed roman string")

    def test_roman_to_int(self):
        for line in roman_list:
            value = reusables.roman_to_int(line[1])
            assert value == line[0], (line, value)

    def test_int_to_words(self):
        for pair in numbers_list:
            assert reusables.int_to_words(pair[0]) == pair[1], \
                "Couldn't translate {0}".format(pair[0])

    def test_bad_ints_to_words(self):
        try:
            reusables.int_to_words("ABC")
        except ValueError:
            pass
        else:
            raise AssertionError("Parsed alphabets")

        try:
            reusables.int_to_words("1.ABC")
        except ValueError:
            pass
        else:
            raise AssertionError("Parsed alphabets")

    def test_european_ints(self):
        for pair in european_numbers:
            assert reusables.int_to_words(pair[0], european=True) == pair[1], \
                "Couldn't translate {0}".format(pair[0])
