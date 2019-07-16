from reusables.shared_variables import ReusablesError

class InvalidInputError(ReusablesError):
    pass


class RetryCountExceededError(ReusablesError):
    pass


def sanitized_input(message="", cast_obj=None, n_retries=-1,
                    error_msg="", valid_input=[], raise_on_invalid=False):
    """
         Function sanitized_input :
         @args
             message: string to show the user (default: "")
             cast_obj: an object to cast the string into. Object must have a __new__
                       method that can take a string as the first positionnal argument
                       and be a subclass of type.
                       The object should raise a ValueError exception if a
                       string can't be cast into that object.
                       cast_obj can also be a tuple or a list, which will
                       chain casts until the end of the list. Casts are chained in
                       reverse order of the list (to mimic the syntax int(float(x))) (default: str)
             n_retries: number of retries. No limit if n_retries < 0 (default: -1)
             error_msg: message to show the user before asking the input again in
                        case an error occurs (default: repr of the exception)
             valid_input: an iterable to check if the result is allowed.
             raise_on_invalid: boolean, wether this function will raise a
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
    retry_cnt = 0

    cast_obj = cast_obj if cast_obj is not None else str
    if isinstance(cast_obj, type):
        cast_objects = (cast_obj, )
    elif isinstance(cast_obj, tuple) or isinstance(cast_obj, list):
        cast_objects = list(cast_obj)
    else:
        raise ValueError("""ValueError: argument 'cast_obj'
                         cannot be of type '{}'""".format(type(cast_obj)))

    if not hasattr(valid_input, '__iter__'):
        valid_input = (valid_input, )
    while (retry_cnt < n_retries) or n_retries < 0:
        try:
            rv = input(message)
            for cast_obj in reversed(cast_objects):
                rv = cast_obj(rv)
            if not valid_input or rv in valid_input:
                return rv
            else:
                raise InvalidInputError("""InvalidInputError: input invalid
                                        in function 'sanitized_input' of {}""".format(__name__))
        except ValueError as e:
            if error_msg:
                print(error_msg)
            else:
                print(repr(e))
            retry_cnt += 1
            continue
        except InvalidInputError as e:
            if raise_on_invalid:
                raise e
            if error_msg:
                print(error_msg)
            else:
                print(repr(e))
            retry_cnt += 1
            continue
    raise RetryCountExceededError("""RetryCountExceededError : count exceeded in
                                  function 'sanitized_input' of {}""".format(__name__))
