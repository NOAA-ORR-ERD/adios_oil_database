"""
Assorted utilities

A few right here:
"""

from math import log10, floor


def sigfigs(x, sig=6):
    return round(x, sig - int(floor(log10(abs(x)))) - 1)


