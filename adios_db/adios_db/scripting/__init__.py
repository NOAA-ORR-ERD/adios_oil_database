"""
Assorted utilities to help with writing scripts that use the oil database
"""

import sys
from pathlib import Path
import json

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample, SampleMetaData
from adios_db.models.oil.properties import Emulsion, EmulsionList
from adios_db.models.oil.physical_properties import DensityPoint


from adios_db.models.oil.location_coordinates import LocationCoordinates

# this brings in all the measurement types
from adios_db.models.common.measurement import *

TEST_DATA_DIR = (Path(__file__)
                 .parent
                 .parent / "test" / "data_for_testing" / "noaa-oil-data")


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
    for fname in sorted(Path(data_dir).rglob("*.json")):
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

data_dir is a where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""

def process_input(USAGE=USAGE, other_flags=()):
    """
    process sys.argv to get the path and whether it's a dry_run or not

    :param USAGE=USAGE: the usage message to return print if there's an
                        error in the input -- default provided

    :returns base_dir, dry_run, other_flags: base_dir is a Path object of the dir passed in.
                                dry_run is True if "dry_run" is on the
                                command line. other_flags is a list of Bools, as to whether
                                the other flags are there.
    """
    try:
        sys.argv.remove("dry_run")
        dry_run = True
    except ValueError:
        dry_run = False
    if isinstance(other_flags, str):
        other_flags = [other_flags]
    others = []
    for flag in other_flags:
        try:
            sys.argv.remove(flag)
            others.append(True)
        except ValueError:
            others.append(False)

    try:
        base_dir = Path(sys.argv[1])
    except IndexError:
        print(USAGE)
        sys.exit()
    if others:
        if len(others) == 1:
            others = others[0]
        return base_dir, dry_run, others
    else:
        return base_dir, dry_run


def find_highest_id(prefix, oil_path):
    """
    find the highest id of the records with a
    given prefix.

    :param prefix: two-char prefix of the IDs

    :param oil_path: Path where the oil JSON files are.

    NOTE: this assumes that the file names match the ID
    """
    records = (oil_path / prefix).glob(f"{prefix}?????.json")
    highest = max(records)
    return highest.stem

