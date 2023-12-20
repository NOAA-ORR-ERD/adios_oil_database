#!/usr/bin/env python
"""
Assign Oil IDs to records
"""
import sys
from pathlib import Path

from adios_db.scripting import get_all_records, Oil

USAGE = """
adios_db_assign_ids PREFIX [dry_run] data_dir, file1, file2, file3, ...

PREFIX is the prefix you want to use: e.g. AD, EC, etc.

you can pass any number of file in, e.g.

XX00012.json

or

XX*.json

Example:

adios_db_assign_ids AD [dry_run] ../noaa-oil-data/data/oil XX/*.json

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():

    try:
        sys.argv.remove("dry_run")
        dry_run = True
    except ValueError:
        dry_run = False

    try:
        prefix = sys.argv[1]
        base_dir = Path(sys.argv[2])
    except IndexError:
        print(USAGE)
        sys.exit()

    infiles = sys.argv[3:]

    print(f"{base_dir=}")
    print(f"{dry_run=}")
    print(f"{prefix=}")
    print(f"{infiles=}")


    # Find the max ID in use:
    max_id = 0
    for oil, pth in get_all_records(base_dir):
        id = oil.oil_id
        if id.startswith(prefix):
            max_id = max(max_id, int(id[len(prefix):]))

    # assign the ids:
    # max_id += 1
    for fname in infiles:
        # file_dir = Path(fname).parent
        max_id += 1
        oil = Oil.from_file(fname)
        id = oil.oil_id
        name = oil.metadata.name
        new_id = f"{prefix}{max_id:05}"
        print(f"assigning: {new_id} to: {name}")
        oil.oil_id = new_id
        (base_dir / prefix).mkdir(exist_ok=True)
        new_fname = base_dir / prefix / f"{new_id}.json"
        if not dry_run:
            print("Saving to:", new_fname)
            oil.to_file(new_fname)
        else:
            print("Nothing saved")

if __name__ == "__main__":
    main()
