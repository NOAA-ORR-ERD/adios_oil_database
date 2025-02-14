"""
script to compare / reconcile product type between two set of data.

if they are different, the new records are updated to match the old ones.

currently hard-coded for where the data are on Chris' machine...

"""

import adios_db.scripting as ads
from pathlib import Path

path_orig = Path("/Users/chris.barker/Hazmat/GitLab/noaa-oil-data-before-CC/data/oil/AD")

path_new = Path("/Users/chris.barker/Hazmat/GitLab/noaa-oil-data/data/oil/AD")

for oil_new, path in ads.get_all_records(path_new):

    ID = oil_new.oil_id
    try:
        oil_orig = ads.Oil.from_file(path_orig / (ID + ".json"))
    except FileNotFoundError:
        continue
    pt_new = oil_new.metadata.product_type
    pt_orig = oil_orig.metadata.product_type
    if oil_new.metadata.product_type != oil_orig.metadata.product_type:
        print("\nPRODUCT TYPES DON'T MATCH")
        print("**** ", oil_new.oil_id, oil_new.metadata.name)
        print(pt_orig, pt_new)
        print("restoring old product_type")
        oil_new.metadata.product_type = pt_orig
        oil_new.to_file(path)







