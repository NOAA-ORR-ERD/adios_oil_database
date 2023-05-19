#!/usr/bin/env python

"""
Script to import data from a CSV file exported from the
NOAA "standard" Excel template.

That template should be in this repo in the "data" folder

"""

import logging
from pathlib import Path
import sys
from adios_db import initialize_console_log
from adios_db.data_sources.noaa_csv.reader import read_csv

USAGE = """
adios_db_import_noaa_csv csv_filename.csv [outfilename.json] [--debug]

Imports a NOAA Standard CSV file, validates it, and writs it out as
a ADIOS Oil Database JSON file.

Optionally provide a filename for the JSON output -- if not provided,
it will be the same as the input, with a ".json" extension.

if "--debug" is on the command line, a LOT of debugging info will be provided.

"""


def main():
    """
    Read the data the CSV file provided on the command line

    export it as a JSON file
    """
    logging.debug("Starting up script")
    if "--debug" in sys.argv:
        initialize_console_log(level='debug')
        sys.argv.remove("--debug")
    try:
        infilename = Path(sys.argv[1])
    except IndexError:
        print("You must provide the filename on the command line")
        print(USAGE)
        sys.exit()

    try:
        outfilename = Path(sys.argv[2])
    except IndexError:
        outfilename = infilename.with_suffix(".json")

    print("Reading:", infilename)
    oil = read_csv(infilename)

    print("Validation Report")
    for msg in oil.validate():
        print(msg)

    print(f"Saving: {outfilename} as JSON")
    oil.to_file(outfilename)

if __name__ == "__main__":
    main()
