#!/usr/bin/env python3
"""
script to go through all the data, and remove entries
in temp-value lists that have a missing value.
"""
import sys

from adios_db.models.oil.cleanup.temp_value import TempValueEmpty
from adios_db.scripting import get_all_records, process_input


USAGE = """
remove_missing_values data_dir [dry_run]

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
        fixer = TempValueEmpty(rec)
        flag, msg = fixer.check()

        if flag is True:
            print(msg)
            print("Cleaning up!")
            msg = fixer.cleanup()
            print(msg)

            if not dry_run:
                print("Saving out:", pth)
                rec.to_file(pth)
            else:
                print("Nothing saved")


if __name__ == "__main__":
    main()
