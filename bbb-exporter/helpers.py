import time
from typing import List


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
