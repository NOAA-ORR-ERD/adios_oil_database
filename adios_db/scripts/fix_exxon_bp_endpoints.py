#!/usr/bin/env python
"""
Add the fraction recovered from a TSV file

NOTE: this is really only designed to be run once, but
      I'm keeping it here as an example for future, similar work
"""
import sys
import csv

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
    # Make BP range open ended for first and last cut
    # vacuum residue
    rec.sub_samples[-1].metadata.boiling_point_range.max_value = None

    # Butane cut:
    rec.sub_samples[1].metadata.boiling_point_range.min_value = None

    rec.to_file(fname)
