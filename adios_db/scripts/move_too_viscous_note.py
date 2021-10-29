#!/usr/bin/env python3

"""
script to move the "Too Viscous" note to comment in EC data
"""

import sys

from adios_db.scripting import get_all_records, process_input


def main():
    base_dir, dry_run = process_input()

    for rec, pth in get_all_records(base_dir):
        print("\n\n******************\n")
        print("processing:", rec.oil_id, rec.metadata.name)
        # loop through the subsamples
        for ss in rec.sub_samples:
            pp = ss.physical_properties
            for itp in pp.interfacial_tension_water:
                if itp.tension.value is not None:
                    try:
                        itp.tension.value = float(itp.tension.value)
                    except ValueError:
                        itp.comment = itp.tension.value
                        itp.tension.value = None

        if not dry_run:
            print("Saving out:", pth)
            rec.to_file(pth)
        else:
            print("Nothing saved")


if __name__ == "__main__":
    main()







