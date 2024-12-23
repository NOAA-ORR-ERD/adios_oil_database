#!/usr/bin/env python
"""
Add the suggested labels to all records, from the add_labels code.
"""
import sys
import csv

from adios_db.models.oil.cleanup.add_labels import get_suggested_labels
from adios_db.scripting import get_all_records, process_input

USAGE = """
adios_db_add_labels data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "replace" is on the command line, existing labels with be replaced
Other wise, new ones will be added, but none removed.

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""

LABELS_NOT_TO_USE = {"Home Heating Oil"}


def add_the_labels():
    # Look for "replace"
    try:
        sys.argv.remove("replace")
        replace = True
    except ValueError:
        replace = False

    base_dir, dry_run = process_input(USAGE)

    with open("labels.csv", 'w') as outfile:
        outfile.write("ID, Name, Product Type, Labels\n")

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

                labels = sorted(set(labels) - LABELS_NOT_TO_USE)

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

    print("output written to: labels.txt")

if __name__ == "__main__":
    add_the_labels()
