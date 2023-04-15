#!/usr/bin/env python
"""
Fixes the unit type of Reid Vapor Pressure -- it was set to mass fraction accidentally
"""
import sys

from adios_db.scripting import get_all_records, process_input


USAGE = """
add_fraction_recovered data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""

base_dir, dry_run = process_input()


for rec, fname in get_all_records(base_dir):
    for ss in rec.sub_samples:
        for prop in ss.industry_properties:
            if prop.name == 'Reid Vapor Pressure':
                print(prop.measurement)
                prop.measurement.unit_type = "pressure"
                print(prop.measurement)

    if dry_run:
        print("not writing anything")
    else:
        print("writing record")
        rec.to_file(fname)
