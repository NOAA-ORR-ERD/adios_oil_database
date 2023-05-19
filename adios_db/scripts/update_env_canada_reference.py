#!/usr/bin/env python
"""
This updates the reference field for Env. Canada records.

We will put some safeguards in the script, but please do not run this on
any other records.
"""
import sys

from adios_db.scripting import get_all_records, process_input

USAGE = """
update_env_canada_reference.py data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def run_through():
    base_dir, dry_run = process_input(USAGE=USAGE)
    
    new_ref = ('Environment and Climate Change Canada, Environment '
               'Canada Crude Oil and Petroleum Product Database, '
               'Environment and Climate Change Canada, 2021.\n\n'
               'url: https://open.canada.ca/data/en/dataset/'
               '53c38f91-35c8-49a6-a437-b311703db8c5')

    for oil, pth in get_all_records(base_dir):
        id = oil.oil_id
        name = oil.metadata.name

        if id[:2] == 'EC':
            print("\nProcessing:", id, name)
            print("changing reference to:", new_ref)
            oil.metadata.reference.reference = new_ref

            if not dry_run:
                print("Saving out:", pth)
                oil.to_file(pth)
            else:
                print("Dry Run: Nothing saved")


if __name__ == "__main__":
    run_through()
