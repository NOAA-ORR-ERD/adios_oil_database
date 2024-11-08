#!/usr/bin/env python
"""
Script to extract all adhesion data from the database, and export to a CSV file.
"""
import sys
import csv

import adios_db.scripting as adb


data_dir, dry_run = adb.process_input()

output_filename = 'adhesion_data.csv'

with open(output_filename, 'w', newline='') as outfile:
    output_writer = csv.writer(outfile, delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)

    output_writer.writerow(["ID", "Name", "Product Type", "Subsample Name", "Needle Adhesion", "unit"])
    # Look through all the oil record files
    for oil, path in adb.get_all_records(data_dir):
        name = oil.metadata.name
        product_type = oil.metadata.product_type
        ID = oil.oil_id
        for sample in oil.sub_samples:
            env = sample.environmental_behavior
            adhesion = env.adhesion
            if adhesion is not None:
                row = [ID, name, product_type, sample.metadata.name, f'{adhesion.value}', f'{adhesion.unit}']
                print(row)
                output_writer.writerow(row)

print("Finished!")
