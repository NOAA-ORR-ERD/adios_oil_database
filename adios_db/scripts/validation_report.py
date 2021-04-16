#!/usr/bin/env python

"""
generates a validation report from a collection of oil JSON files
"""

import sys
import datetime
import json

from adios_db.scripting import get_all_records

USAGE = """
validation_report data_dir [save]

Generate a validation report for the JSON files in data_dir

If "save" is on the command line, the. status will be updated
with the latest validation.
"""

def main():

    try:
        sys.argv.remove("save")
        save = True
    except ValueError:
        save = False

    try:
        base_dir = sys.argv[1]
    except IndexError:
        print(USAGE)
        sys.exit(1)

    with open("adios_db_validation.txt", 'w', encoding="utf-8") as outfile:
        outfile.write("Validation of data in: \n")
        outfile.write(base_dir)
        outfile.write("\n")
        outfile.write(str(datetime.datetime.now()))
        outfile.write("\n\n")
        for oil, pth in get_all_records(base_dir):
            print("\n\n******************\n")
            print(f"processing: {oil.oil_id}: {oil.metadata.name}")

            oil.reset_validation()
            print(oil.status)
            if oil.status:
                outfile.write(f"{oil.oil_id}: {oil.metadata.name}\n")
                for msg in oil.status:
                    outfile.write(f"    {msg}\n")
            if save:
                with open(pth, 'w', encoding='utf-8') as datafile:
                        json.dump(oil.py_json(), datafile, indent=4)


if __name__ == "__main__":
    main()
