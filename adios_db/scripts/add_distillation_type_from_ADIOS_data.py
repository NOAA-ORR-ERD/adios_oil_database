#!/usr/bin/env python
"""
find data in old ADIOS DB with emulsifiation constant

"""
import sys
from pathlib import Path
import math
import adios_db.scripting as ads


adios_data = Path("../data/OilLib.txt")
json_data_dir = Path("../../../noaa-oil-data/data/oil/AD/")


def process(adios_data, json_data_dir):
    # Read the data
    with open(adios_data, encoding='latin-1') as infile:
        infile.readline()
        header = infile.readline().split("\t")
        header_map = {name.strip(): idx for idx, name in enumerate(header)}

        num_weight = num_vol = num_unknown = 0

        for rec in infile:
            rec = rec.split("\t")
            ID = rec[header_map['ADIOS_Oil_ID']].strip()
            name = rec[header_map['Oil_Name']].strip()
            dist_type = rec[header_map['Cut_Units']].strip()

            # Add the info to the records
            path = json_data_dir / (ID + ".json")
            oil = ads.Oil.from_file(path)
            dist = oil.sub_samples[0].distillation_data

            if dist.cuts: # there is some data there
                print(ID, name, "D type:", dist_type)

                if dist_type == "volume":
                    dist.type = "Volume Fraction"
                    num_vol += 1
                elif dist_type == 'weight':
                    dist.type = 'Mass Fraction'
                    num_weight += 1
                elif dist_type == "":
                    dist.type = None
                    num_unknown += 1
                    print("***** One with NONE")
                else:
                    raise ValueError("unknown data in record")

        if dry_run:
            print("Nothing saved")
        else:
            print("writing to file")
            oil.to_file(path)

    print(f"{num_unknown=}")
    print(f"{num_weight=}")
    print(f"{num_vol=}")


if __name__ == "__main__":
    if "dry_run" in sys.argv:
        dry_run = True
    else:
        dry_run = False

    process(adios_data, json_data_dir)
