#!/usr/bin/env python
"""
This script re-imports the Exxon data from the Excel spreadsheets,
and then updates the Industry Properties with the newly imported data.

Not replacing the whole thing, as then we'd lose any other changes we made.

note: all paths are hard-coded as this only needs to be run once.
"""
import sys
from pathlib import Path

import adios_db.scripting as ads
from adios_db.data_sources.exxon_assays.reader import ExxonDataReader
from adios_db.data_sources.exxon_assays.mapper import ExxonMapper

EXXON_DATA_DIR = Path("../../../noaa-oil-data/data/oil/EX/")

USAGE = """
updated_exxon_industry_properties [save]

if "save" is specified the data will be saved, otherwise not.

"""


def the_exxon_data():
    index_file = "../data/exxon_assays/index.txt"
    reader = ExxonDataReader(index_file)

    for rec in reader.get_records():
        yield ExxonMapper(rec)


def load_old_exxon_data():
    print("loading the data in:", EXXON_DATA_DIR)
    all_recs = {}

    for fname in EXXON_DATA_DIR.glob("*.json"):
        print("loading:", fname)
        all_recs[fname.parts[-1][:-5]] = ads.Oil.from_file(fname)

    # {fname.parts[-1][:-5] : ads.Oil.from_file(fname)
    #             for fname in EXXON_DATA_DIR.glob("*.json")}

    return all_recs


def find_rec_by_name(recs, name):
    for rec in recs:
        if rec.metadata.name == name:
            return rec

    return None


def get_next_id(all_recs):
    ids = list(all_recs.keys())
    ids.sort()
    id_nums = [int(id[2:]) for id in ids]
    print(id_nums)

    return f'EX{max(id_nums) + 1:05d}'


if __name__ == "__main__":
    old_recs = load_old_exxon_data()
    new_records = []

    for rec in the_exxon_data():
        name = rec.metadata.name
        name = name
        id = rec.oil_id

        old_rec = find_rec_by_name(old_recs.values(), name)
        if old_rec is not None:
            print(f"new_name: {name}, old_name: {old_rec.metadata.name}")
            print(f"new_id: {id}, old_id: {old_rec.oil_id}")
            # putting in hew industry_properties

            # print("New Industry Properties:")
            # for prop in rec.sub_samples[0].industry_properties:
            #     print(prop)
            # print("Old Industry Properties:")
            # for prop in old_rec.sub_samples[0].industry_properties:
            #     print(prop)

            for new_ss, old_ss in zip(rec.sub_samples, old_rec.sub_samples):
                old_ss.industry_properties = new_ss.industry_properties
            # print("Old Industry Properties after resetting:")
            # for prop in old_rec.sub_samples[0].industry_properties:
            #     print(prop)

            if "save" in sys.argv:
                filename = EXXON_DATA_DIR / (old_rec.oil_id + ".json")
                print("saving:", filename)
                old_rec.to_file(filename)
        else:
            print(f"no: {name} in the old data")
            new_records.append(name)
            new_id = get_next_id(old_recs)
            rec.oil_id = new_id
            old_recs[new_id] = rec

            if "save" in sys.argv:
                filename = EXXON_DATA_DIR / (old_rec.oil_id + ".json")
                print("saving:", filename)
                rec.to_file(filename)

    print("The new data, not found in the old:")
    print(new_records)
