#!/usr/bin/env python
"""
Script to update the test data from the "canonical" source data
"""
import sys
from pathlib import Path
from shutil import copyfile

HERE = Path(__file__).parent


def main():
    try:
        noaa_data_dir = sys.argv[1]
    except IndexError:
        print("you must pass in the dir of the NOAA data: "
              "probably the 'oil' dir")
        sys.exit()

    # find records to update:

    test_data_dir = HERE / "../test/data_for_testing/noaa-oil-data/oil"

    filenames = test_data_dir.rglob("*.json")

    for path in filenames:
        filename = Path().joinpath(*path.parts[-2:])
        source_file = noaa_data_dir / filename
        dest_file = test_data_dir / filename

        print("copying:", source_file)
        print("to:", dest_file)
        copyfile(source_file, dest_file)
