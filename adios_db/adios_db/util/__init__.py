"""
Assorted utilities

A few right here:
"""
from math import log10, floor


def sigfigs(x, sig=6):
    try:
        if isinstance(x, str):
            x = float(x)
        return round(x, sig - int(floor(log10(abs(x)))) - 1)
    except (ValueError, TypeError):
        return x


def strip(value):
    try:
        return value.strip()
    except (ValueError, TypeError, AttributeError):
        return value


class BufferedIterator():
    """
    An iterator that can have stuff put back

    Give it an iterable, and it will create an iterator that iterates,
    but you can push things back on to be returned in future next calls.

    In the common case, this would be used to put back an item, but you
    could use it more generally.

    See the test code in test_utilities

    """
    def __init__(self, iterable):
        self.iter = iter(iterable)
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self.buffer:
            return self.buffer.pop()
        return next(self.iter)

    def push(self, item):
        self.buffer.append(item)

