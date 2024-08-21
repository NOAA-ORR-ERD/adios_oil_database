#!/usr/bin/env python
"""
Ads the "Gas Oil" label to every record that had a "Diesel" label
"""

# the scripting module has a few utilities and the
# core Python objects you may need for scripting
# calling it "adb" for easy typing
import adios_db.scripting as adb
from adios_db.models.oil.cleanup.add_labels import get_suggested_labels

base_dir, dry_run = adb.process_input()
outfile = open("fuel_oil_labels.txt", "w")
hfo = []
ifo = []
neither = []
both = []
# Loop through all the JSON files in the given directory:
print("Processing files in:", base_dir)
num_changed = 0
for oil, path in adb.get_all_records(base_dir):
    # print("Processing", oil.metadata.name)
    if oil.metadata.product_type == "Residual Fuel Oil":
        labels = get_suggested_labels(oil)
        if "HFO" in labels:
            hfo.append(f"{oil.oil_id}, {oil.metadata.API=},{oil.metadata.name=}\n")
            hfo.append(f"{labels=}\n\n")

        if "IFO" in labels:
            ifo.append(f"{oil.oil_id}, {oil.metadata.API=}, {oil.metadata.name=}\n")
            ifo.append(f"{labels=}\n\n")
        if "HFO" in labels and "IFO" in labels:
            both.append(f"{oil.oil_id}, {oil.metadata.API=}, {oil.metadata.name=}\n")
            both.append(f"{labels=}\n\n")
        else:
            neither.append(f"{oil.oil_id}, {oil.metadata.API=}, {oil.metadata.name=}\n")
            neither.append(f"{labels=}\n\n")
    
    # select the desired product types:
    # labels = set(oil.metadata.labels)
    # if "Diesel" in labels:
    #     num_changed += 1
    #     labels.add("Gas Oil")
    #     print("Adding Gas Oil to:", oil.metadata.name)
    #     if not dry_run:
    #         oil.metadata.labels[:] = sorted(labels)
    #         print("saving to:", path)
    #         oil.to_file(path)
    #     else:
    #         print("Nothing saved")

# print(f"{num_changed} records found")

outfile.write("HFO\n")
outfile.writelines(hfo)
outfile.write("IFO\n")
outfile.writelines(hfo)
outfile.write("Both\n")
outfile.writelines(both)
outfile.write("Neither\n")
outfile.writelines(neither)