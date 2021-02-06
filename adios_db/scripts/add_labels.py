#!/usr/bin/env python

"""
Add the suggested labels to all records, from the add_labels code.

"""

import sys
import csv

from adios_db.models.oil.cleanup.add_labels import get_suggested_labels
from adios_db.scripting import get_all_records

USAGE = """
add_labels data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def add_the_labels():
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
        pt = oil.metadata.product_type

        print("\nFor Oil:", id, name)
        try:
            labels = get_suggested_labels(oil)
            print(labels)

            if not dry_run:
                print("Saving out:", pth)
                oil.metadata.labels = list(labels.union(oil.metadata.labels))
                oil.to_file(pth)
            else:
                print("Nothing saved")
        except:  # if anything goes wrong, we won't add an labels
            print("Something went wrong -- no labels")


if __name__ == "__main__":
    add_the_labels()
