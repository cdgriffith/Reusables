class InvalidInputError(Exception):
    pass


class RetryCountExceededError(Exception):
    pass


def sanitized_input(message="", cast_obj=None, n_retries=-1,
                    error_msg="", valid_input=[], raise_on_invalid=False):
    """
         Function sanitized_input :
         @args
             message: string to show the user (default: "")
             cast_obj: an object to cast the string into. Object must have an __init__
                       method that can take a string as the first positionnal argument.
                       object should raise a ValueError exception if a string can't be cast into
                       that object (default: str)
             n_retries: number of retries. No limit if n_retries < 0 (default: -1)
             error_msg: message to show the user before asking the input again in
                        case an error occurs (default: repr of the exception)
             valid_input: an iterable to check if the result is allowed.
        @returns
           rv : string literal casted into the cast_obj as per that object's rules.
           raises : RetryCountExceededError if the retry count has exceeded the n_retries limit.
    """
    raw = ""
    retry_cnt = 0
    cast_obj = cast_obj if cast_obj is not None else str
    if not hasattr(valid_input, '__iter__'):
        valid_input = (valid_input, )
    while (retry_cnt < n_retries) or n_retries < 0:
        try:
            raw = input(message)
            rv = cast_obj(raw)
            if not valid_input or rv in valid_input:
                return rv
            else:
                raise InvalidInputError(f"""InvalidInputError: input invalid
                                        in function 'sanitized_input' of {__name__}""")
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
    raise RetryCountExceededError(f"""RetryCountExceededError : count exceeded in
                                  function 'sanitized_input' of {__name__}""")
