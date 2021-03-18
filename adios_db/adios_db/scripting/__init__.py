"""
Assorted utilities to help with writing scripts that use the oil database
"""

import sys
from pathlib import Path
import json

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample, SampleMetaData
from adios_db.models.oil.properties import Emulsion, EmulsionList
from adios_db.models.oil.location_coordinates import LocationCoordinates

# this brings in all the measurement types
from adios_db.models.common.measurement import *


def get_all_records(data_dir):
    """
    gets all the records from the JSON data stored in gitLab

    This is a generator that gets all the records, returning them one by one
    as record, path pairs

    :param data_dir: the directory that holds the data

    The record returned is an Oil object

    Use as such::
       for oil, path in get_all_records(data_dir):
            work_with_the_record

    """
    dir = Path(data_dir)
    for fname in sorted(dir.rglob("*.json")):
        with open(fname, encoding='utf-8') as jfile:
            try:
                pyjson = json.load(jfile)
            except Exception:
                print("Something went wrong loading:", fname)
                raise
        rec = Oil.from_py_json(pyjson)

        yield rec, fname

USAGE = """
do_something.py:  data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def process_input(USAGE=USAGE):
    try:
        sys.argv.remove("dry_run")
        dry_run = True
    except ValueError:
        dry_run = False

    try:
        base_dir = sys.argv[1]
    except IndexError:
        print(USAGE)
        sys.exit()

    return base_dir, dry_run