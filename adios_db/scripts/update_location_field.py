#!/usr/bin/env python
"""
This updates the location field for more normailzation

it changes "texas" to "Texas, USA" it could do more :-)
"""
import sys

from adios_db.scripting import get_all_records, process_input

orig_location = "texas"
new_location = "Texas, USA"

USAGE = """
update_location_field.py data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def run_through():
    base_dir, dry_run = process_input(USAGE=USAGE)

    for oil, pth in get_all_records(base_dir):
        id = oil.oil_id
        name = oil.metadata.name
        location = oil.metadata.location

        if location.lower() == orig_location:
            print("\nProcessing:", id, name)
            print("changing location to:", new_location)

            oil.metadata.location = new_location

            if not dry_run:
                print("Saving out:", pth)
                oil.to_file(pth)
            else:
                print("Dry Run: Nothing saved")


if __name__ == "__main__":
    run_through()
