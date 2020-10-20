#!/usr/bin/env python3

"""
script to go through all the data, and add an API if one is not already there
"""

import sys
from pathlib import Path

from oil_database.models.oil.oil import Oil
import json

class Fake():
    oil_id = "XXXXXXXXX"


def get_all_records(data_dir):
    """
    a generator that gets all the records, returning them one by one
    as record, path pairs

    :param data_dir: the directory that holds the data
    """
    dir = Path(data_dir)
    for fname in dir.rglob("*.json"):
        with open(fname, encoding='utf-8') as jfile:
            pyjson = json.load(jfile)
        rec = Oil(pyjson)
        yield rec, fname


if __name__ == "__main__":
    try:
        base_dir = sys.argv[1]
    except IndexError:
        print("you must pass in the base dir where the data are stored")
        sys.exit(1)

    for rec, pth in get_all_records(base_dir):
        print("\n\n******************\n")
        print(type(rec))
        print(type(rec.oil_id))
        print("processing:", rec.oil_id)
        print("API is:", rec.metadata.API)
        break



