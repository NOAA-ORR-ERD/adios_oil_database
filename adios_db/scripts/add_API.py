#!/usr/bin/env python3
"""
script to go through all the data, and add an API if one is not already there
"""
import sys

from adios_db.models.oil.cleanup.density import FixAPI
from adios_db.scripting import get_all_records, process_input


USAGE = """
add_API data_dir [dry_run]

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
        fixer = FixAPI(rec)
        flag, msg = fixer.check()

        if flag is True:
            print(msg)
            print("Cleaning up!")
            fixer.cleanup()
            print("API is now:", rec.metadata.API)

            if not dry_run:
                print("Saving out:", pth)
                rec.to_file(pth)
            else:
                print("Nothing saved")
        elif flag is False:
            print(msg)
            print("It's a:", rec.metadata.product_type)
            print("Densities are:", rec.sub_samples[0].physical_properties.densities)
        else:
            print(msg)


if __name__ == "__main__":
    main()
