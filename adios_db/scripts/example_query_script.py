#!/usr/bin/env python
"""
Example script for how to query the database and
export a subset of the data to a CSV file

As is, this exports viscosity data for crude oils
"""

# the scripting module has a few utilities and the
# core Python objects you may need for scripting
# calling it "adb" for easy typing
import adios_db.scripting as adb

base_dir, dry_run = adb.process_input()

# create a new text file for output
outfile = open("example_data.csv", 'w', encoding="utf-8")

# write the header row:
outfile.write('Name, ID, Dynamic Viscosity, unit, reference temp, unit\n')


# Loop through all the JSON files in the given directory:
print("Extracting from data:", base_dir)
for oil, path in adb.get_all_records(base_dir):
    print("\n**** ", oil.metadata.name)

    # select the desired product types:
    if oil.metadata.product_type in {"Crude Oil NOS",
                                     "Condensate",
                                     "Tight Oil",
                                     }:
        print(">> This is a Crude of some sort")

        fresh = oil.sub_samples[0]

        try:
            dvis = fresh.physical_properties.dynamic_viscosities[0]
        except IndexError:
            print("IndexError -- skipping")
            # no viscosity, why bother writing it out?
            continue  # skip to next one in loop

        # Make sure output is all in the same units.
        viscosity = dvis.viscosity.converted_to("mPa.s")
        ref_temp = dvis.ref_temp.converted_to("C")

        # write a row in the csv file
        outfile.write(f'"{oil.metadata.name}", {oil.oil_id}'
                      f', {viscosity.value}'
                      f', {viscosity.unit}'
                      f', {ref_temp.value}'
                      f', {ref_temp.unit}'
                      '\n')
    else:
        print(">> This is NOT a Crude NOS")
