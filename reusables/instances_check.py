try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


def and_instances(obj, *instance_types):
    """
        Tests if obj is an instance of all supplied instance types.

        :param obj: the object to test
        :param *instance_types: an iterable of instance types to test for.

        :return: True if the object is an instance of all the supplied instance types,
                 False otherwise.
    """
    if len(instance_types) == 1 and isinstance(instance_types[0], Iterable):
        instance_types = instance_types[0]

    rv = [isinstance(obj, instance_type) for instance_type in instance_types]
    return False not in rv


def or_instances(obj, *instance_types):
    """
        Tests if obj is an instance of any supplied instance types.

        :param obj: the object to test
        :param *instance_types: an iterable of instance types to test for.

        :return: True if the object is an instance of any of the supplied
                 instance types, False otherwise.
    """
    if len(instance_types) == 1 and isinstance(instance_types[0], Iterable):
        instance_types = instance_types[0]

    rv = [isinstance(obj, instance_type) for instance_type in instance_types]
    return True in rv


are_instances = or_instances
