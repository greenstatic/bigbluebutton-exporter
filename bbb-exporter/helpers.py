import os
import time
from typing import List, Optional


def execution_duration(fun):
    """
    Calculates the duration the function 'fun' takes to execute.
    execution_duration returns a wrapper function to which you pass your arguments.

    Example: execution_duration(my_function)(my_first_param, my_second_param)

    The result of the wrapper function will be a tuple, where the fist value is the
    return value of your function and the second is the execution time in seconds expressed
    as a float.
    """
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = fun(*args, **kwargs)
        exec_dur = time.time() - t1

        return result, exec_dur

    return wrapper


def valid_api_base_url(url: str) -> bool:
    return len(url) > 0 and url[-1] == "/"


def validate_api_base_url(url: str) -> str:
    if not valid_api_base_url(url):
        raise ValueError("Invalid API_BASE_URL, must end with trailing slash")

    return url


class HistogramBucketHelper:
    """
    A helper class that helps us create a histogram metric by saving buckets and their associated values.
    """

    _buckets = []
    sum = 0

    def __init__(self, buckets: List[float]):
        self._buckets = list(map(lambda x: [x, 0], buckets))

    def add(self, val):
        for entry in self._buckets:
            if entry[0] >= val:
                entry[1] += 1

        self.sum += val

    def get_buckets(self):
        """
        Returns list of buckets that contains a list, where the first element is the size of the bucket as a string
        and the second element is the value.
        Inf is represented as '+Inf' as per Prometheus requirements.
        """
        return list(map(lambda x: (str(x[0]) if x[0] != float("inf") else "+Inf", x[1]), self._buckets))


def string_list_to_int_list(xs: str) -> List[int]:
    if xs == '':
        return []
    return [int(i) for i in xs.split(",")]


def int_list_greater_than_zero(l: List[int]) -> bool:
    """
    Return True if every element in list is >= 0, else False
    """
    for i in l:
        if i < 0:
            return False
    return True


def validate_buckets(xs: str) -> List[int]:
    try:
        buckets = string_list_to_int_list(xs)
    except ValueError:
        raise ValueError("Non-integer value in list of buckets")

    if not int_list_greater_than_zero(buckets):
        raise ValueError("List of buckets contain int less than 0")

    return buckets


def verify_recordings_base_dir_exists() -> bool:
    import settings
    return os.path.exists(settings.recordings_metrics_base_dir)


def str_to_bool_or_none(s: str) -> Optional[bool]:
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False

    return None
