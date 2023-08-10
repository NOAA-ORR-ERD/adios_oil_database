#!/usr/bin/env python
"""
Ads the "Gas Oil" label to every record that had a "Diesel" label
"""

# the scripting module has a few utilities and the
# core Python objects you may need for scripting
# calling it "adb" for easy typing
import adios_db.scripting as adb

base_dir, dry_run = adb.process_input()

# Loop through all the JSON files in the given directory:
print("Processing files in:", base_dir)
num_changed = 0
for oil, path in adb.get_all_records(base_dir):
    # print("Processing", oil.metadata.name)

    # select the desired product types:
    labels = set(oil.metadata.labels)
    if "Diesel" in labels:
        num_changed += 1
        labels.add("Gas Oil")
        print("Adding Gas Oil to:", oil.metadata.name)
        if not dry_run:
            oil.metadata.labels[:] = sorted(labels)
            print("saving to:", path)
            oil.to_file(path)
        else:
            print("Nothing saved")

print(f"{num_changed} records found")


