#!/usr/bin/env python
"""
This script looks at the distillation type, and sets the unit_type properly

"""
import adios_db.scripting as ads
from adios_db.models.oil.cleanup.distillation import FixCutUnitType


json_data_dir, dry_run = ads.process_input()

# Read the data
for rec, pth in ads.get_all_records(json_data_dir):
    print("processing:", rec.oil_id)
    fixer = FixCutUnitType(rec)
    flag, msg = fixer.check()

    if flag is True:
        print(msg)
        print("Cleaning up!")
        fixer.cleanup()

        if not dry_run:
            print("Saving out:", pth)
            rec.to_file(pth)
        else:
            print("Nothing saved")
