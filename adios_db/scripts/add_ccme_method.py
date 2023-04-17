#!/usr/bin/env python
"""
Add the method to CCME data
"""
import sys

from adios_db.scripting import get_all_records
from adios_db.models.oil import ccme


USAGE = """
add_ccme_method data_dir [dry_run]

NOTE: this will also clear out empty CCME fractions

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

        CCME = oil.sub_samples[0].CCME

        print("\nFor Oil:", id, name)
        print("CCME:", CCME)
        print()

        if (CCME.F1.value is None and
                CCME.F2.value is None and
                CCME.F3.value is None and
                CCME.F4.value is None):
            # put in an empty CCME
            print("replacing CCME with an empty one")
            oil.sub_samples[0].CCME = ccme.CCME()
        else:
            # Add the method
            print("adding the method")
            oil.sub_samples[0].CCME.method = "ESTS 5.03/x.x/M"
        # except:  # if anything goes wrong, we won't add an labels
        #     print("Something went wrong -- no change to CCME record")
        #     return

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Dry Run: Nothing saved")


if __name__ == "__main__":
    add_the_method()
