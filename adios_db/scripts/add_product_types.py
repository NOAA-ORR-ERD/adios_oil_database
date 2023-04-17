#!/usr/bin/env python
"""
Add the product types to all records, from a CSV file

NOTE: this is really only designed to be run once, but
      I'm keeping it here as an example for future, similar work
"""
import sys
import csv

from adios_db.models.oil.product_type import PRODUCT_TYPES
from adios_db.scripting import get_all_records


USAGE = """
add_product_types data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def read_the_csv_file(csv_name):
    print("Reading product types from:", csv_name)
    with open(csv_name, encoding="utf-8") as csvfile:
        data = {(row[0][:2] + row[0][-5:]): row[1:]
                for row in csv.reader(csvfile, delimiter="\t")}

    print(f"loaded {len(data) - 1} records")

    return data


def add_them(data):
    missing = open("missing_records.csv", 'w', encoding="utf-8")
    name_mismatch = open("name_mismatch_records.csv", 'w', encoding="utf-8")

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
        ID = oil.oil_id

        try:
            row = data[ID]
        except KeyError:
            print(f"{ID} not in the spreadsheet")
            missing.write(",".join([ID, oil.metadata.name]))
            name_mismatch.write("\n")
            continue

        name = row[0]

        print("Processing:", ID)

        if name == oil.metadata.name:
            pt = row[6].strip()
            print("Product Type:", pt)

            if pt:
                if pt not in PRODUCT_TYPES:
                    raise ValueError(f"not a Valid Product type: {pt}")

            oil.metadata.product_type = pt
        else:
            print("Name doesn't match!", name, oil.metadata.name)
            name_mismatch.write(",".join([ID, oil.metadata.name, name]))
            name_mismatch.write("\n")

        print(oil.oil_id, oil.metadata.name, oil.metadata.product_type)

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Nothing saved")


if __name__ == "__main__":
    # data = read_the_csv_file("Evaluation_Of_Oil_Type_List - temp.tsv")
    data = read_the_csv_file("Evaluation_Of_Oil_Type_List_January2021.tsv")
    add_them(data)
