#!/usr/bin/env python3

"""
script to go through all the data, and add an API if one is not already there

This could use a bit more polish:
  - flag to have it report what it will do, but not do it
  - pass in a single file or the whole dir

Testing! -- not entirely sure if it breaks the records!
"""

import sys
from pathlib import Path
import json

from oil_database.models.oil.oil import Oil
from oil_database.models.cleanup.density import FixAPI
from oil_database.scripting import get_all_records


class Fake():
    oil_id = "XXXXXXXXX"

if __name__ == "__main__":
    try:
        base_dir = sys.argv[1]
    except IndexError:
        print("you must pass in the base dir where the data are stored")
        sys.exit(1)

    for rec, pth in get_all_records(base_dir):
        # print("\n\n******************\n")
        # print("processing:", rec.oil_id)
        # print("API is:", rec.metadata.API)
        fixer = FixAPI(rec)
        flag, msg = fixer.check()
        if flag is True:
            print(msg)
            print("Cleaning up!")
            fixer.cleanup()
            print("API is now:", rec.metadata.API)
            print("Saving out:", pth)
            with open(pth, 'w', encoding='utf-8') as outfile:
                json.dump(rec.py_json(), outfile, indent=4)









