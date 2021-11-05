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
from adios_db.models.oil.validation import (unpack_status,
                                            is_only_ignored,
                                            ERRORS_TO_IGNORE)

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

    write_reports(base_dir, save)





def write_reports(base_dir, save):

    validation_by_record = {}
    validation_by_error = {}
    validation_by_record_rev = {}
    validation_by_error_rev = {}


    # validate all the records:
    for oil, pth in get_all_records(base_dir):
        print("\n\n******************\n")
        print(f"processing: {oil.oil_id}: {oil.metadata.name}")

        oil.reset_validation()
        # unpack into a dict for easier processing
        status = unpack_status(oil.status)
        if status: print(status)
        if status:
            if (oil.review_status.status.lower() == "review complete"
                    or is_only_ignored(status)):
                validation_by_record_rev[oil.oil_id] = (oil.metadata.name,
                                                        oil.status)
            else:
                validation_by_record[oil.oil_id] = (oil.metadata.name,
                                                    oil.status)
        for error_code, msgs in status.items():
            issues = "\n".join(f"\n``{oil.oil_id}`` -- {oil.metadata.name}:\n\n    {msg}\n"
                               for msg in msgs)
            if (oil.review_status.status.lower() == "review complete"
                or error_code in ERRORS_TO_IGNORE):
                validation_by_error_rev.setdefault(error_code, []).append(issues)
            else:
                validation_by_error.setdefault(error_code, []).append(issues)
        if save:
            with open(pth, 'w', encoding='utf-8') as datafile:
                json.dump(oil.py_json(), datafile, indent=4)

    with open("validation_by_record.rst", 'w',
              encoding="utf-8") as outfile1:
        write_header(outfile1, base_dir)
        write_by_record(outfile1, validation_by_record)
        write_header_rev(outfile1)
        write_by_record(outfile1, validation_by_record_rev)

    # write out the validation by error
    with open("validation_by_error.rst", 'w', encoding="utf-8") as outfile:
        write_header(outfile, base_dir)
        write_by_error(outfile, validation_by_error)
        write_header_rev(outfile)
        write_by_error(outfile, validation_by_error_rev)


def write_by_record(outfile1, validation_by_record):
    for oil_id, info in validation_by_record.items():
        name, status = info
        outfile1.write(f"\n``{oil_id}``: {name}\n")
        for msg in status:
            # validation_by_record.setdefault(msg.split(":")[0], []).append(
            #                       f"\n``{oil_id}`` -- {name}:\n\n    {msg}\n")
            outfile1.write(f" |    {msg}\n")


def write_by_error(outfile, validation_by_error):
    for code, errors in sorted(validation_by_error.items(), key=itemgetter(0)):
        header = f"{code}: ({len(errors)} records affected)"
        outfile.write(f"\n\n{header}\n{'=' * len(header)}\n")
        outfile.writelines(errors)


def write_header(of, base_dir):
    of.write("\n####################################\n")
    of.write(  "ADIOS Oil Database Validation Report\n")
    of.write(  "####################################\n\n")
    of.write("Validation of data in: \n\n")
    of.write(f"``{base_dir.absolute()}``\n\n")
    of.write("**Generated:** "
             f"{datetime.datetime.now().strftime('%h %d, %Y - %H:00')}\n\n")


def write_header_rev(outfile):
    outfile.write("\n\n############\n"
                      "Known Issues\n"
                      "############\n\n"
                  "The rest of these are records that have been reviewed, but still \n"
                  "have issues that are known and may never be resolved\n")




if __name__ == "__main__":
    main()
