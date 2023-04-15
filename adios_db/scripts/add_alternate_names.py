#!/usr/bin/env python
"""
Add the alternate names to all records, from a CSV file

NOTE: this is really only designed to be run once, but
      I'm keeping it here as an example for future, similar work
"""
import sys
import csv

from adios_db.scripting import get_all_records, process_input


USAGE = """
add_alternate_names data_dir [dry_run]

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

    base_dir, dry_run = process_input(USAGE)

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
            anames = [name.strip() for name in row[10].strip().split(",")]
            # clean out the duplicates
            anames = [n for n in anames if n.lower() not in name.lower()]

            if anames:
                oil.metadata.alternate_names = anames
                print("Adding:", oil.oil_id, oil.metadata.name, oil.metadata.alternate_names)

                if not dry_run:
                    print("Saving out:", pth)
                    oil.to_file(pth)
                else:
                    print("Nothing saved")
        else:
            print("Name doesn't match!", name, oil.metadata.name)
            name_mismatch.write(",".join([ID, oil.metadata.name, name]))
            name_mismatch.write("\n")


if __name__ == "__main__":
    data = read_the_csv_file("Evaluation_Of_Oil_Type_List - temp.tsv")
    add_them(data)
