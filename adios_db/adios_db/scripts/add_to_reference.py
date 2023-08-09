#!/usr/bin/env python
"""
This simply runs all the JSON records through the Oil object

A way to "normalize" it all.

Ideally, it doesn't change a thing, but if the Oil object changes,
then it might have to update something.
"""

from adios_db.scripting import Oil, process_input

USAGE = """
add_to_reference data_dir [dry_run]

Add soemthign to the reference

What that is is hard-coded in this script

Use at the moment:

adding:
https://media.amsa.gov.au/media-release/amsa-conducting-marine-environment-low-sulphur-fuel-oil-study
to AMSA LSFO references
"""


def run_through():
    base_dir, dry_run = process_input(USAGE=USAGE)

    print("Processing JSON files in:", base_dir)
    pth = None
    for pth in sorted(base_dir.rglob("*.json")):
        print("processing:", pth)

        try:
            oil = Oil.from_file(pth)
        except Exception as ex:
            print("Something went wrong loading:", pth)
            print(ex)
            raise


        old_reference = oil.metadata.reference.reference.strip()
        old_reference_year = oil.metadata.reference.year

        if old_reference.startswith("Trevor Gilbert"):
            oil.metadata.reference.year = 2022
            oil.metadata.reference.reference = ("Trevor Gilbert, Response to Very Low Sulphur Marine Fuel Oil Spills, "
                                                "Report to Australian Maritime Safety Authority 2022, "
                                                "Scientific & Environmental Associates Australia\n"
                                                "(https://media.amsa.gov.au/media-release/amsa-conducting-marine-environment-low-sulphur-fuel-oil-study)"
                                                )

        if not dry_run:
            print("Saving out:", pth)
            oil.to_file(pth)
        else:
            print("Dry Run: Nothing saved")

    if pth is None:
        print("No files were found in:", base_dir)


if __name__ == "__main__":
    run_through()
