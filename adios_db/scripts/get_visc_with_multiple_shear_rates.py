#!/usr/bin/env python
"""
script to see what viscosity data are available
"""
import sys

import adios_db.scripting as dbs

data_dir = sys.argv[1]

records_with_kvis_data = {}
records_with_dvis_data = {}

outfile = open("viscosity_data_multiple_shear.csv", 'w', encoding="utf-8")
outfile.write('Name, "Product Type", ID, "Kin. Values", "Dyn. Values"\n')

records_with_dist_cuts = []

base_dir, dry_run = dbs.process_input()

have_shear = {}
num = 0
# Look through all the data for viscosity
for oil, path in dbs.get_all_records(data_dir):

    print(oil.metadata.name)
    fresh = oil.sub_samples[0]

    vis = fresh.physical_properties.kinematic_viscosities
    if not vis:
        vis = fresh.physical_properties.dynamic_viscosities


    if len(vis) < 2:
        continue
    print(vis)
    num += 1

    has_shear = 0
    for v in vis:
        print("shear rate:", v.shear_rate)
        if v.shear_rate is not None:
            has_shear += 1
    if has_shear > 1:
        PP = oil.sub_samples[0].physical_properties.pour_point
        PP = PP if PP is None else f"{PP.measurement.value}{PP.measurement.unit}"
        data = [oil.oil_id, f"{oil.metadata.name}\n", f"PP:{PP}"]
        for v in vis:
            data.append((f"{v.ref_temp.value}{v.ref_temp.unit}",
                         f"{v.viscosity.value} {v.viscosity.unit}",
                         v.shear_rate if v.shear_rate is None else f"{v.shear_rate.value} {v.shear_rate.unit}"))
        have_shear[oil.oil_id] = data
    else:
        continue

    # if num > 2:
    #     break

for ID, rec in have_shear.items():
    print()
    print(rec[0], rec[1], rec[2], rec[3])
    for d in rec[4:]:
        print("        ", d)


#     records_with_kvis_data.setdefault(len(kvis), set()).add(oil.metadata.name)
#     records_with_dvis_data.setdefault(len(dvis), set()).add(oil.metadata.name)
    
#     numkvis = len(kvis)
#     numdvis = len(dvis)
#     if numkvis >= 3 or numdvis >= 3:
#         outfile.write(f'"{oil.metadata.name}", "{oil.metadata.product_type}", {oil.oil_id}, {len(kvis)}, {len(dvis)}\n')





# print("Available viscosity Data:")
# print("num_values   Kinematic   Dynamic")
# for i in range(10):
#     try:
#         print(f"{i}.               {len(records_with_kvis_data[i])}        {len(records_with_dvis_data[i])}")
#     except KeyError:
#         pass

# print("records with dist cuts but only one viscosity:")
# # for n in records_with_dist_cuts:
# #     print(n)

# print(f"A total of {len(records_with_dist_cuts)} records that could be used "
#       "with the Abu-Eishah:1999 approach for viscosity with temp")

# print("Report Written to: viscosity_data.csv")

