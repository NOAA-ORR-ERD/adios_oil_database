#!/usr/bin/env python
"""
Add the method to ESTS Hydrocarbon fractions data

It should be: "ESTS 5.03/x.x/M"

it also removed the field if it's empty.
"""
import sys

from adios_db.scripting import get_all_records
from adios_db.models.oil import ccme


USAGE = """
add_ESTS_method data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def add_the_method():
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
        id = oil.oil_id
        name = oil.metadata.name
        pt = oil.metadata.product_type

        fractions = oil.sub_samples[0].ESTS_hydrocarbon_fractions

        print("\nFor Oil:", id, name)
        print("ESTS_HydroCarbonFractions:", fractions)
        print()

        if (not fractions.aromatics and
                not fractions.GC_TPH and
                not fractions.saturates):
            print("ESTS_hydrocarbon_fractions empty: removing")
            oil.sub_samples[0].ESTS_hydrocarbon_fractions = None
        else:
            print("adding the method")
            fractions.method = "ESTS 5.03/x.x/M"

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Dry Run: Nothing saved")


if __name__ == "__main__":
    add_the_method()
