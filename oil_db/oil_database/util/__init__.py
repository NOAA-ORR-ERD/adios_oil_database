"""
Assorted utilities

A few right here:
"""

from math import log10, floor


def sigfigs(x, sig=6):
    try:
        return round(x, sig - int(floor(log10(abs(x)))) - 1)
    except (ValueError, TypeError):
        return x


def strip(value):
    try:
        return value.strip()
    except (ValueError, TypeError, AttributeError):
        return value
