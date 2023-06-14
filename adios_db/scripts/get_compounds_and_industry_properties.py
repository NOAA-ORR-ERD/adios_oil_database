#!/usr/bin/env python
"""
Script to walk the /data/ folder of the noaa-oil-data project and gather the
compound names and industry property names from all the oil records.

From these names we create two unique lists (sets) and write them out to a
.csv file
"""
import sys
import csv
from itertools import zip_longest

import adios_db.scripting as dbs


data_dir = sys.argv[1]
output_filename = 'compounds_and_industry_properties.csv'
compound_names = set()
industry_properties = set()


def add_compound_names(sample):
    compound_names.update({c.name for c in sample.compounds})


def add_industry_properties(sample):
    industry_properties.update({c.name for c in sample.industry_properties})


def write_data_rows(writer):
    writer.writerow([
        'Compound Name',
        'Industry Property',
    ])

    for name, prop in zip_longest(sorted(compound_names, key=str.lower),
                                  sorted(industry_properties, key=str.lower)):
        writer.writerow([name, prop])

with open(output_filename, 'w', newline='') as compare_fd:
    output_writer = csv.writer(compare_fd, delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)

    # Look through all the oil record files
    for oil, path in dbs.get_all_records(data_dir):
        print(path, oil.metadata.name)

        for sample in oil.sub_samples:
            add_compound_names(sample)
            add_industry_properties(sample)

    print(f'\n{len(compound_names)} Compound Names:')
    print(f'\n{len(industry_properties)} Industry Properties:')
    write_data_rows(output_writer)

print("Finished!")
