#!/usr/bin/env python3
"""
script to go through all the data, and add an API if one is not already there

"""
import sys

from adios_db.models.oil.cleanup.density import FixAPI
from adios_db.scripting import get_all_records, process_input

USAGE = """
update_API data_dir [dry_run]

This script will re-compute the API from the provided density data.

Caution: this will overwrite whatever API value was there:
 -- you may well not want to do that!

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():
    base_dir, dry_run = process_input()

    for rec, pth in get_all_records(base_dir):
        print("\n\n******************\n")
        print("processing:", rec.oil_id, rec.metadata.name)
        # first check if API passes validation:
        msgs = rec.validate()
        has_API = False
        for msg in msgs:
            if "API" in msg:
                print(msg)
                has_API = True
        if not has_API:
            continue

        print("There was an API related Validation Error")

        old_API = rec.metadata.API
        rec.metadata.API = None
        fixer = FixAPI(rec)
        flag, msg = fixer.check()

        if flag is True:
            print(msg)
            print("Cleaning up!")
            fixer.cleanup()
            print("API is now:", rec.metadata.API)
        elif flag is False:
            print(msg)
            print("It's a:", rec.metadata.product_type)
            print("Densities are:", rec.sub_samples[0].physical_properties.densities)
        else:
            print(msg)

        if rec.metadata.API is None:
            rec.metadata.API = old_API

        print(f"Changed API from: {old_API} to {rec.metadata.API}")

        if not dry_run:
            print("Saving out:", pth)
            rec.to_file(pth)
        else:
            print("Nothing saved")


if __name__ == "__main__":
    main()
