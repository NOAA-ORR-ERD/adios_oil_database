#!/usr/bin/env python
"""
Assign Oil IDs to records
"""
import sys
import csv

from adios_db.models.oil.cleanup.add_labels import get_suggested_labels
from adios_db.scripting import get_all_records, process_input

USAGE = """
adios_db_assign_ids PREFIX [dry_run] file1, file2, file3, ...

PREFIX is the prefix you want to use: e.g. AD, EC, etc.

you can pass any number of file in, e.g.

XX00012.json

or

XX*.json

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():
    base_dir, dry_run = process_input(USAGE)

    for oil, pth in get_all_records(base_dir):
        id = oil.oil_id
        name = oil.metadata.name
        pt = oil.metadata.product_type

        print("\nFor Oil:", id, name)
        print("product type:", pt)

        try:
            prev_labels = oil.metadata.labels
            labels = get_suggested_labels(oil)
            print("Previous: ", prev_labels)
            print("suggested:", labels)

            if not replace:
                labels = sorted(set(labels + prev_labels))

            print("new:      ", labels)
            outfile.write(f"{id}, {name}, {pt}, {str(labels).strip('{}')}\n")

            if not dry_run:
                print("Saving out:", pth)
                oil.metadata.labels = sorted(labels)
                oil.to_file(pth)
            else:
                print("Nothing saved")
        except Exception as exp:  # if anything goes wrong, we won't add an labels
            print("Something went wrong -- no labels")
            print(exp)

if __name__ == "__main__":
    main()
