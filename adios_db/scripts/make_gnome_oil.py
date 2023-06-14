#!/usr/bin/env python
"""
script to see which oils are suitable for gnome
"""
import sys

import adios_db.scripting as dbs
from adios_db.computation.gnome_oil import make_gnome_oil

data_dir = sys.argv[1]

#outfile = open("gnome_oil_info.csv", 'w', encoding="utf-8")
#outfile.write('Name, ID, "Product Type"\n')

# Make gnome_oil from all of the records
for oil, path in dbs.get_all_records(data_dir):
    print(oil.metadata.name)
    fresh = oil.sub_samples[0]

    try:
        go = make_gnome_oil(oil)
    except Exception as err:
        print("failed to make gnome oil ",err,oil.metadata.name,oil.oil_id,oil.metadata.product_type)

    #outfile.write(f'"{oil.metadata.name}", {oil.oil_id}, {len(kvis)}, {len(dvis)}\n')
