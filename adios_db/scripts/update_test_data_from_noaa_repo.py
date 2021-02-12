#!/usr/bin/env python

"""
Script to update the test data from the "canonical" source data

Designed to be run from this dir

"""

import sys
from pathlib import Path
from shutil import copyfile

noaa_data_dir = sys.argv[1]

# find records to update:

test_data_dir = Path("../adios_db/test/test_session/test_data/oil/")

filenames = test_data_dir.rglob("*.json")

for path in filenames:
    filename = Path().joinpath(*path.parts[-2:])
    source_file = noaa_data_dir / filename
    dest_file = test_data_dir / filename

    print("copying:", source_file)
    print("to:", dest_file)
    copyfile(source_file, dest_file)



