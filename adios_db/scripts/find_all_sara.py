#!/usr/bin/env python
"""
Script to find all crude oil records with SARA data in the database
"""

# the scripting module has a few utilities and the
# core Python objects you may need for scripting
# calling it "adb" for easy typing
import adios_db.scripting as adb

base_dir, dry_run = adb.process_input()

# create a new text file for output
outfile = open("sara_data.csv", 'w', encoding="utf-8")

# write the header row:
outfile.write('Name, ID, API, Saturates, Aromatics, Asphaltenes, Resins\n')


# Loop through all the JSON files in the given directory:
print("Extracting from data:", base_dir)
for oil, path in adb.get_all_records(base_dir):
    print("\n**** ", oil.metadata.name)

    # select the desired product types:
    if oil.metadata.product_type in {"Crude Oil NOS",
                                     # "Condensate",
                                     # "Tight Oil",
                                     }:

        fresh = oil.sub_samples[0]

        SARA = fresh.SARA

        # Make sure output is all in the same units.
        print(f"SARA is {SARA}")
        if SARA:
            # write a row in the csv file

            outfile.write(f'"{oil.metadata.name}", {oil.oil_id}, {oil.metadata.API}')
            outfile.write(f',{"" if SARA.saturates is None else SARA.saturates.converted_to("fraction").value}' )
            outfile.write(f',{"" if SARA.aromatics is None else SARA.aromatics.converted_to("fraction").value}' )
            outfile.write(f',{"" if SARA.resins is None else SARA.resins.converted_to("fraction").value}' )
            outfile.write(f',{"" if SARA.asphaltenes is None else SARA.asphaltenes.converted_to("fraction").value}' )
            outfile.write('\n')
