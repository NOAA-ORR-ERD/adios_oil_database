#!/usr/bin/env python
"""
script to see what viscosity data are available
"""
import sys

import adios_db.scripting as dbs

data_dir = (r"C:\Users\rintaro.moriyasu\Oil Databases\noaa-oil-data\data\oil")
                
#data_dir = sys.argv[1]

records_with_kvis_data = {}
records_with_dvis_data = {}

outfile = open("viscosity_data.csv", 'w', encoding="utf-8")
outfile.write('Name, "Product Type", ID, "Kin. Values", "Dyn. Values"\n')

records_with_dist_cuts = []

# Look through all the data for viscosity
for oil, path in dbs.get_all_records(data_dir):
    print(oil.metadata.name)
    fresh = oil.sub_samples[0]

    kvis = fresh.physical_properties.kinematic_viscosities
    dvis = fresh.physical_properties.dynamic_viscosities

    records_with_kvis_data.setdefault(len(kvis), set()).add(oil.metadata.name)
    records_with_dvis_data.setdefault(len(dvis), set()).add(oil.metadata.name)
    
    numkvis = len(kvis)
    numdvis = len(dvis)
    if numkvis >= 3 or numdvis >= 3:
        outfile.write(f'"{oil.metadata.name}", "{oil.metadata.product_type}", {oil.oil_id}, {len(kvis)}, {len(dvis)}\n')





print("Available viscosity Data:")
print("num_values   Kinematic   Dynamic")
for i in range(10):
    try:
        print(f"{i}.               {len(records_with_kvis_data[i])}        {len(records_with_dvis_data[i])}")
    except KeyError:
        pass

print("records with dist cuts but only one viscosity:")
# for n in records_with_dist_cuts:
#     print(n)

print(f"A total of {len(records_with_dist_cuts)} records that could be used "
      "with the Abu-Eishah:1999 approach for viscosity with temp")

print("Report Written to: viscosity_data.csv")

