#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import reusables

from .common_test_data import *


class TestReuseNamespace(BaseTestClass):

    def test_namespace(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        namespace = reusables.Namespace(**test_dict)
        assert namespace.key1 == test_dict['key1']
        assert dict(getattr(namespace, 'Key 2')) == test_dict['Key 2']
        setattr(namespace, 'TEST_KEY', 'VALUE')
        assert namespace.TEST_KEY == 'VALUE'
        delattr(namespace, 'TEST_KEY')
        assert 'TEST_KEY' not in namespace.to_dict(), namespace.to_dict()
        assert isinstance(namespace['Key 2'].Key4, reusables.Namespace)
        assert "'key1': 'value1'" in str(namespace)
        assert repr(namespace).startswith("<Namespace:")

    def test_namespace_modifiy_at_depth(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}

        namespace = reusables.Namespace(**test_dict)
        assert 'key1' in namespace
        assert 'key2' not in namespace
        namespace['Key 2'].new_thing = "test"
        assert namespace['Key 2'].new_thing == "test"
        namespace['Key 2'].new_thing += "2"
        assert namespace['Key 2'].new_thing == "test2"
        assert namespace['Key 2'].to_dict()['new_thing'] == "test2", namespace['Key 2'].to_dict()
        assert namespace.to_dict()['Key 2']['new_thing'] == "test2"
        namespace.__setattr__('key1', 1)
        assert namespace['key1'] == 1
        namespace.__delattr__('key1')
        assert 'key1' not in namespace

    def test_error_namespace(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}

        namespace = reusables.Namespace(**test_dict)
        try:
            getattr(namespace, 'hello')
        except AttributeError:
            pass
        else:
            raise AssertionError("Should not find 'hello' in the test dict")

    def test_namespace_tree(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        namespace = reusables.Namespace(**test_dict)
        result = namespace.tree_view(sep="    ")
        assert result.startswith("key1\n") or result.startswith("Key 2\n")
        assert "Key4" in result and "    Value5\n" not in result

    def test_namespace_from_dict(self):
        ns = reusables.Namespace.from_dict({"k1": "v1", "k2": {"k3": "v2"}})
        assert ns.k2.k3 == "v2"

    def test_namespace_from_bad_dict(self):
        try:
            ns = reusables.Namespace.from_dict('{"k1": "v1", '
                                               '"k2": {"k3": "v2"}}')
        except TypeError:
            assert True
        else:
            assert False, "Should have raised type error"

    def test_config_namespace(self):
        g = {"b0": 'no',
             "b1": 'yes',
             "b2": 'True',
             "b3": 'false',
             "b4": True,
             "i0": '34',
             "f0": '5.5',
             "f1": '3.333',
             "l0": '4,5,6,7,8',
             "l1": '[2 3 4 5 6]'}

        cns = reusables.ConfigNamespace(g)
        assert cns.list("l1", spliter=" ") == ["2", "3", "4", "5", "6"]
        assert cns.list("l0", mod=lambda x: int(x)) == [4, 5, 6, 7, 8]
        assert not cns.bool("b0")
        assert cns.bool("b1")
        assert cns.bool("b2")
        assert not cns.bool("b3")
        assert cns.int("i0") == 34
        assert cns.float("f0") == 5.5
        assert cns.float("f1") == 3.333
        assert cns.getboolean("b4"), cns.getboolean("b4")
        assert cns.getfloat("f0") == 5.5
        assert cns.getint("i0") == 34
        assert cns.getint("Hello!", 5) == 5
        assert cns.getfloat("Wooo", 4.4) == 4.4
        assert cns.getboolean("huh", True) is True
        assert cns.list("Waaaa", [1]) == [1]
        repr(cns)


# noinspection PyTypeChecker
class TestProtectedDict(BaseTestClass):

    def test_create_protected_dict(self):
        """
        Validate a protected dictionary can be created with the format of a
        normal dictionary.
        """
        test_dict = {"Test 1": 1, "Test 2": 2, "Test 3": 3}
        test_protected = reusables.ProtectedDict({"Test 1": 1,
                                                  "Test 2": 2,
                                                  "Test 3": 3})
        str(test_protected)
        repr(test_protected)
        for k, v in test_protected.items():
            assert k in test_dict.keys()
            assert test_dict[k] == v

    def test_copy_protected_dict(self):
        """
        Validate that a copy of a protected dictionary is just a normal
        dictionary, and no longer a protected dictionary.
        """
        test_protected = reusables.ProtectedDict(a=1, b=2, c=3)
        copy = test_protected.copy()
        assert test_protected == copy
        assert isinstance(copy, dict)
        assert not isinstance(copy, reusables.ProtectedDict)

    def test_add_key(self):
        """
        Validate that you cannot add a new key value pair to a protected
        dictionary.
        """
        test_protected = reusables.ProtectedDict({"Test 1": 1,
                                                  "Test 2": 2,
                                                  "Test 3": 3})

        try:
            test_protected["Test 4"] = 4
        except AttributeError:
            pass
        else:
            assert False

    def test_change_value(self):
        """
        Validate that you cannot change the value of a normal key value pair
        in a protected dictionary.
        """
        test_protected = reusables.ProtectedDict({"Test 1": 1,
                                                  "Test 2": 2,
                                                  "Test 3": 3})

        try:
            test_protected["Test 1"] = 10
        except AttributeError:
            pass
        else:
            assert False

    def test_change_sub_dict(self):
        """
        Validate that stored objects, such as a sub dictionary, may be
        altered in a protected dictionary.
        """
        test_protected = reusables.ProtectedDict({"Test 1": {"a": 1, "b": 2},
                                                  "Test 2": 2, })

        test_protected["Test 1"]["a"] = 3
        assert test_protected["Test 1"]["a"] == 3

    def test_unhashable(self):
        """
        Validate that a protected dictionary with a sub dictionary is not
        hashable.
        """
        test_protected = reusables.ProtectedDict({"Test 1": {"a": 1, "b": 2},
                                                  "Test 2": 2, })
        try:
            hash(test_protected)
        except TypeError:
            pass
        else:
            assert False

    def test_hashable(self):
        """
        Validate that a protected dictionary hash is an integer type.
        Validate that two protected dictionary objects with the same data
        have the same hash value.
        Validate that two protected dictionary objects with different data
        have different hash values.
        """
        test_dict_one = reusables.ProtectedDict({"Test 1": 1,
                                                 "Test 2": 2,
                                                 "Test 3": 3})
        test_dict_two = reusables.ProtectedDict({"Test 1": 1,
                                                 "Test 2": 2,
                                                 "Test 3": 3})
        test_dict_three = reusables.ProtectedDict({"Test 4": 4,
                                                   "Test 5": 5,
                                                   "Test 6": 6})
        assert isinstance(hash(test_dict_one), int)
        assert isinstance(hash(test_dict_two), int)
        assert isinstance(hash(test_dict_three), int)
        assert hash(test_dict_two) == hash(test_dict_one)
        assert hash(test_dict_three) != hash(test_dict_one)
