try:
    from collections.abc import Iterable, Callable
except ImportError:
    from collections import Iterable, Callable

from reusables.shared_variables import ReusablesError


class InvalidInputError(ReusablesError):
    pass


class RetryCountExceededError(ReusablesError):
    pass


def _get_input(prompt):
    return input(prompt)


def sanitized_input(message="", cast_as=None, number_of_retries=-1,
                    error_message="", valid_input=(), raise_on_invalid=False):
    """
         Function sanitized_input :
         @args
             message: string to show the user (default: "")
             cast_as: an object to cast the string into. Object must have a __new__
                       method that can take a string as the first positional argument
                       and be a subclass of type.
                       The object should raise a ValueError exception if a
                       string can't be cast into that object.
                       cast_obj can also be a tuple or a list, which will
                       chain casts until the end of the list. Casts are chained in
                       reverse order of the list (to mimic the syntax int(float(x))) (default: str)
             number_of_retries: number of retries. No limit if n_retries == -1 (default: -1)
             error_message: message to show the user before asking the input again in
                            case an error occurs (default: repr of the exception).
                            Can include {error}.
             valid_input: an iterable to check if the result is allowed.
             raise_on_invalid: boolean, whether this function will raise a
                               reusables.InvalidInputError if the input doesn't match
                               the valid_input argument.
        @returns
            rv : string literal casted into the cast_obj as per that object's rules.
            raises : RetryCountExceededError if the retry count has exceeded the n_retries limit.
        @examples
            integer = sanitized_input("How many apples?", int,
                      error_msg="Please enter a valid number")
                >>> returns an int, will prompt until the user enters an integer.
            validated = sanitized_input(">>>", valid_input=["string"], raise_on_invalid=True)
                >>> returns the value "string", and will raise InvalidInputError otherwise.
            chain_cast = sanitized_input(">>>", cast_obj=[int, float])
                >>> returns an int, prompts like '2.3' won't raise a ValueError Exception.
    """
    retry_count = 0

    cast_as = cast_as if cast_as is not None else str
    cast_objects = list(cast_as) if isinstance(cast_as, Iterable) else (cast_as, )
    for cast_obj in cast_objects:
        if not isinstance(cast_obj, Callable):
            raise ValueError("ValueError: argument 'cast_as'"
                             "cannot be of type '{}'".format(type(cast_as)))

    if not hasattr(valid_input, '__iter__'):
        valid_input = (valid_input, )
    while retry_count < number_of_retries or number_of_retries == -1:
        try:
            rv = _get_input(message)
            for cast_obj in reversed(cast_objects):
                rv = cast_obj(rv)
            if not valid_input or rv in valid_input:
                return rv
            else:
                raise InvalidInputError("InvalidInputError: input invalid"
                                        "in function 'sanitized_input' of {}".format(__name__))
        except ValueError as e:
            print(error_message.format(error=e.message) if error_message else e.message)
            retry_count += 1
            continue
        except InvalidInputError as e:
            if raise_on_invalid:
                raise e
            print(error_message.format(error=e.message) if error_message else e.message)
            retry_count += 1
            continue
    raise RetryCountExceededError("RetryCountExceededError : count exceeded in"
                                  "function 'sanitized_input' of {}".format(__name__))
