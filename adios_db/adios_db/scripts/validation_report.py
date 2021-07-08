#!/usr/bin/env python

"""
generates a validation report from a collection of oil JSON files
"""

import sys
import datetime
import json
from pathlib import Path
from operator import itemgetter

from adios_db.scripting import get_all_records

USAGE = """
adios_validate data_dir [save]

Validation reports for the JSON files in data_dir

These reports are in RST format.

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
        base_dir = Path(sys.argv[1])
    except IndexError:
        print(USAGE)
        sys.exit(1)

    validation = {}

    with (open("validation_by_record.rst", 'w', encoding="utf-8") as outfile1,
          open("validation_by_error.rst", 'w', encoding="utf-8") as outfile2):
        for of in (outfile1, outfile2):
            of.write("\n####################################\n")
            of.write("ADIOS Oil Database Validation Report\n")
            of.write("####################################\n\n")
            of.write("Validation of data in: \n\n")
            of.write(f"``{base_dir.absolute()}``\n\n")
            of.write("**Generated:** "
                     f"{datetime.datetime.now().strftime('%h %d, %Y -- %H00')}\n\n")
        for oil, pth in get_all_records(base_dir):
            print("\n\n******************\n")
            print(f"processing: {oil.oil_id}: {oil.metadata.name}")

            oil.reset_validation()
            print(oil.status)
            if oil.status:
                outfile1.write(f"\n``{oil.oil_id}``: {oil.metadata.name}\n")
                for msg in oil.status:
                    validation.setdefault(msg.split(":")[0], []).append(
                                          f"\n``{oil.oil_id}`` -- {oil.metadata.name}:\n\n    {msg}\n")
                    outfile1.write(f" |    {msg}\n")
            if save:
                with open(pth, 'w', encoding='utf-8') as datafile:
                    json.dump(oil.py_json(), datafile, indent=4)
        # write out the report by Error Code:
        for code, errors in sorted(validation.items(), key=itemgetter(0)):
            header = f"{code}: ({len(errors)} records affected)"
            outfile2.write(f"\n\n{header}\n{'=' * len(header)}\n")
            outfile2.writelines(errors)


if __name__ == "__main__":
    main()
