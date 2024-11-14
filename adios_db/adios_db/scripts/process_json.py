#!/usr/bin/env python
"""
This simply runs all the JSON records through the Oil object

A way to "normalize" it all.

Ideally, it doesn't change a thing, but if the Oil object changes,
then it might have to update something.
"""

from adios_db.scripting import Oil, process_input

USAGE = """
adios_db_process_json data_dir [dry_run] [strip_status]

Process a collection of JSON files -- they are loaded into
the adios_db Oil object, then saved out a again.

This will "normalize" the JSON, and raise an error if a
file can not be loaded.

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes. So that's a good way to check that the JSON
is valid without changing anything.

If "strip_status" is on the command line, it will strip the status and gnome_compatible flags.
"""


def run_through():
    base_dir, dry_run, strip_status = process_input(USAGE=USAGE, other_flags = "strip_status")

    print("Processing JSON files in:", base_dir)
    if strip_status:
        print("stripping the status info")
    pth = None
    for pth in sorted(base_dir.rglob("*.json")):
        print("processing:", pth)

        try:
            oil = Oil.from_file(pth)
        except Exception as ex:
            print("Something went wrong loading:", pth)
            print(ex)
            raise

        if strip_status:
            oil.status = []
            oil.metadata.gnome_suitable = None

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Dry Run: Nothing saved")

    if pth is None:
        print("No files were found in:", base_dir)


if __name__ == "__main__":
    run_through()
