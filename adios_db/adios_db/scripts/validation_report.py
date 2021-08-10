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

    validation_by_record = {}
    validation_by_error = {}
    validation_by_record_rev = {}
    validation_by_error_rev = {}

    def write_header(of):
        of.write("\n####################################\n")
        of.write("ADIOS Oil Database Validation Report\n")
        of.write("####################################\n\n")
        of.write("Validation of data in: \n\n")
        of.write(f"``{base_dir.absolute()}``\n\n")
        of.write("**Generated:** "
                 f"{datetime.datetime.now().strftime('%h %d, %Y -- %H00')}\n\n")

    # validate all the records:
    for oil, pth in get_all_records(base_dir):
        print("\n\n******************\n")
        print(f"processing: {oil.oil_id}: {oil.metadata.name}")

        oil.reset_validation()
        print(oil.status)
        if oil.status:
            if oil.review_status.status.lower() == "review complete":
                validation_by_record_rev[oil.oil_id] = oil.status
            else:
                validation_by_record[oil.oil_id] = oil.status
        for msg in oil.status:
            issues = f"\n``{oil.oil_id}`` -- {oil.metadata.name}:\n\n    {msg}\n"
            if oil.review_status.status.lower() == "review complete":
                validation_by_record_rev.setdefault(msg.split(":")[0], []).append(issues)
            else:
                validation_by_record.setdefault(msg.split(":")[0], []).append(issues)
        if save:
            with open(pth, 'w', encoding='utf-8') as datafile:
                json.dump(oil.py_json(), datafile, indent=4)


    with open("validation_by_record.rst", 'w', encoding="utf-8") as outfile1:
        write_header(outfile1)

        outfile1.write(f"\n``{oil.oil_id}``: {oil.metadata.name}\n")
        for msg in oil.status:
            validation_by_record.setdefault(msg.split(":")[0], []).append(
                                  f"\n``{oil.oil_id}`` -- {oil.metadata.name}:\n\n    {msg}\n")
            outfile1.write(f" |    {msg}\n")


    # write out the validation by error
    with open("validation_by_error.rst", 'w', encoding="utf-8") as outfile:
        write_header(outfile)
        # write out the report by Error Code:
        for code, errors in sorted(validation_by_record.items(), key=itemgetter(0)):
            header = f"{code}: ({len(errors)} records affected)"
            outfile.write(f"\n\n{header}\n{'=' * len(header)}\n")
            outfile.writelines(errors)




if __name__ == "__main__":
    main()
