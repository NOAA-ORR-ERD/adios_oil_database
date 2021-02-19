#!/usr/bin/env python

"""
This simply runs all the JSON records through the Oil object

A way to "normalize" it all.

Ideally, it doesn't change a thing, but if the Oil object changes,
then it might have to update something.
"""

import sys

from adios_db.scripting import get_all_records

USAGE = """
run_through_oil_object.py data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def run_through():
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

    for oil, pth in get_all_records(base_dir):

        id = oil.oil_id
        name = oil.metadata.name

        print("\nProcessing:", id, name)

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Dry Run: Nothing saved")



if __name__ == "__main__":
    run_through()



