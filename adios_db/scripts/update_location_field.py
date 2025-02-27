#!/usr/bin/env python
"""
This updates the location field for more normailzation

It changes any of a list of existing locations to a new location.

In this case, "Gulf of Mexico, USA" (and variants) to "Gulf of America"

Other updates could be done by editing:
orig_locations
new_location
"""

import sys

from adios_db.scripting import get_all_records, process_input

orig_locations = ("Gulf of Mexico", "USA, Gulf of Mexico", "Gulf of Mexico, USA", "Gulf of Mexico")
new_location = "Gulf of America"


USAGE = """
update_location_field.py data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""

def normalize(name):
    name = name.lower().strip()
    name = " ".join(name.split())
    return name

def run_through():
    base_dir, dry_run = process_input(USAGE=USAGE)

    for oil, pth in get_all_records(base_dir):
        id = oil.oil_id
        name = oil.metadata.name
        location = oil.metadata.location
        for orig in orig_locations:
            if normalize(location) == normalize(orig):
                match = True
                break
        else:
            match = False
        if match:
            print("\nProcessing:", id, name)
            print("location was:", location)
            print("changing location to:", new_location)

            oil.metadata.location = new_location

            if not dry_run:
                print("Saving out:", pth)
                oil.to_file(pth)
            else:
                print("Dry Run: Nothing saved")


if __name__ == "__main__":
    run_through()
