import sys
import numpy as np

from adios_db.scripting import get_all_records, process_input


USAGE = """
add_fraction_recovered data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""

outfile = open("diesel_dist_fraction.tsv", 'w')
outfile.write("ID\tName\tnumber of cuts\tfraction below 250C\n")

base_dir, dry_run = process_input()


for rec, fname in get_all_records(base_dir):
    if not rec.metadata.product_type == "Distillate Fuel Oil":
        continue

    if not "diesel" in rec.metadata.name.lower():
        continue

    print(rec.metadata.name)
    dist_data = rec.sub_samples[0].distillation_data.cuts

    if not dist_data:
        continue

    data = ((cut.fraction.converted_to('%').value,
             cut.vapor_temp.converted_to('C').value) for cut in dist_data)
    frac, temp = list(zip(*data))

    if temp[0] >= 250 or temp[-1]<= 250:
        continue

    frac_evap = np.interp(250, temp, frac)
    outfile.write(f"{rec.oil_id}\t{rec.metadata.name}\t")
    outfile.write(f"{len(dist_data)} cuts\t")
    outfile.write(f"{frac_evap:.0f}\t%\n")

outfile.close()
