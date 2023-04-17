#!/usr/bin/env python
"""
Add the fraction recovered from a TSV file

NOTE: this is really only designed to be run once, but
      I'm keeping it here as an example for future, similar work
"""
import sys
import csv

from adios_db.models.oil.product_type import PRODUCT_TYPES
from adios_db.scripting import get_all_records
from adios_db.scripting import Concentration


USAGE = """
add_fraction_recovered data_dir [dry_run]

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

    num_none = 0
    num_one = 0
    num_less_than_one = 0
    num_fraction = 0

    for oil, pth in get_all_records(base_dir):
        ID = oil.oil_id

        try:
            row = data[ID]
        except KeyError:
            print(f"{ID} not in the spreadsheet")
            missing.write(",".join([ID, oil.metadata.name]))
            missing.write("\n")
            continue

        name = row[0]
        print("Processing:", ID, name)

        fraction_recovered = row[3].strip()

        if not fraction_recovered:
            print("no data for this one")
            continue

        print(f"{fraction_recovered=}")

        for ss in oil.sub_samples:
            dist_data = ss.distillation_data
            print(dist_data.fraction_recovered)

            if fraction_recovered == 'None':
                dist_data.fraction_recovered = None
                num_none += 1
            elif fraction_recovered == "<1":
                dist_data.fraction_recovered = Concentration(max_value=1.0, unit="fraction")
                num_less_than_one += 1
            else:
                try:
                    val = float(fraction_recovered)
                    dist_data.fraction_recovered = Concentration(value=val, unit="fraction")

                    if val == 1.0:
                        num_one += 1
                    else:
                        num_fraction += 1
                except ValueError:
                    raise

            if dist_data.fraction_recovered is not None:
                print("********************")
                print("after adding, frac_recovered:")
                print(dist_data.fraction_recovered)

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Nothing saved")

    print(f"{num_none=}")
    print(f"{num_one=}")
    print(f"{num_less_than_one=}")
    print(f"{num_fraction=}")


if __name__ == "__main__":
    data = read_the_csv_file("DistillationFraction.tsv")
    add_them(data)
