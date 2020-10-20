#!/usr/bin/env python3

"""
script to go through all the data, and add an API if one is not already there
"""

import sys
from pathlib import Path

def get_all_records(dir):
    """
    a generator that gets all the records, returning them one by one
    as record, path pairs

    :param dir: the directory that holds the data
    """
    dir = Path(dir)
    for fname in dir.rglob():
        yield fname


if __name__ == "__main__":
    base_dir = sys.argv[1]

    for rec, pth in get_all_records(dir):
        print("processing:", rec.oil_id)

