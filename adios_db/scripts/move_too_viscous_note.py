#!/usr/bin/env python3
"""
script to move the "Too Viscous" note to comment in EC data
"""
import sys

from adios_db.scripting import get_all_records, process_input


def move_ift_note(ift):
    for itp in ift:
        if itp.tension.value is not None:
            try:
                itp.tension.value = float(itp.tension.value)
            except ValueError:
                itp.comment = itp.tension.value
                itp.tension.value = None

        if itp.tension.standard_deviation is not None:
            try:
                itp.tension.standard_deviation = \
                    float(itp.tension.standard_deviation)
            except ValueError:
                itp.comment = itp.tension.standard_deviation
                itp.tension.standard_deviation = None


def main():
    base_dir, dry_run = process_input()

    for rec, pth in get_all_records(base_dir):
        print("\n\n******************\n")
        print("processing:", rec.oil_id, rec.metadata.name)

        # loop through the subsamples
        for ss in rec.sub_samples:
            pp = ss.physical_properties
            move_ift_note(pp.interfacial_tension_water)
            move_ift_note(pp.interfacial_tension_air)
            move_ift_note(pp.interfacial_tension_seawater)

        if not dry_run:
            print("Saving out:", pth)
            rec.to_file(pth)
        else:
            print("Nothing saved")


if __name__ == "__main__":
    main()
