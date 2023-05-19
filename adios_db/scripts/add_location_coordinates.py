#!/usr/bin/env python
"""
Adds location coordinates from a data file
"""
import sys
from ast import literal_eval
from pathlib import Path

from adios_db.scripting import Oil, LocationCoordinates, process_input


USAGE = """
update_location_field.py data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def run_through():
    base_dir, dry_run = process_input(USAGE=USAGE)

    # read the data file
    with open("ADIOS_Locations.csv") as infile:
        infile.readline()
        data = {}

        for line in infile:
            if line.strip():
                line = line.strip().split("|")
                line = [s.strip() for s in line]
                ID, __, type, coords, __ = line
                coords = literal_eval(coords)
                data[ID] = (type, coords)

    for id, coord_info in data.items():
        pth = Path(base_dir) / id[:2] / (id + ".json")
        oil = Oil.from_file(pth)
        name = oil.metadata.name
        oil.metadata.location_coordinates = LocationCoordinates(*coord_info)

        print("\nProcessing:", id, name)
        print("adding:", coord_info)

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Dry Run: Nothing saved")


if __name__ == "__main__":
    run_through()
