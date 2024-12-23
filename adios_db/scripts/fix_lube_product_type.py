#!/usr/bin/env python3
"""
Script to set the product type to Lube OIl for oils that have "Lubricating" in name, but hare set to crude_oil NOS
"""
import sys

from adios_db.models.oil.cleanup.density import FixAPI
from adios_db.scripting import get_all_records, process_input


USAGE = """
fix_lub_product_type [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():
    base_dir, dry_run = process_input()

    for rec, pth in get_all_records(base_dir):
        # print("processing:", rec.oil_id, rec.metadata.name)
        name = rec.metadata.name
        product_type = rec.metadata.product_type
        changed = False
        if "lubricat" in name.lower():
            changed = True
            # print("\n\n******************\n")
            # print("processing:", rec.oil_id, rec.metadata.name)
            if product_type not in {"Dielectric Oil", "Lube Oil"}:
                # print("Record appears to have wrong product type")
                # print(name, product_type)
                # print(rec.metadata.labels)
                # print("Fixing: ")
                rec.metadata.product_type = "Lube Oil"
                # print(rec.metadata.product_type, rec.metadata.labels)
        if rec.metadata.product_type == "Lube Oil":
            changed = True
            # print("/n/n Already Lube Oil")
            # print("labels:", rec.metadata.labels)
            labels = sorted(set(rec.metadata.labels) | {'Lube Oil', 'Refined Product'})
            # print("New:", labels)
            rec.metadata.labels = labels

        if changed:
            print("\n\n******************\n")
            print("processing:", rec.oil_id, rec.metadata.name)

            print(rec.metadata.product_type, rec.metadata.labels)

            if not dry_run:
                print("Saving out:", pth)
                rec.to_file(pth)
            else:
                print("Nothing saved")


if __name__ == "__main__":
    main()
