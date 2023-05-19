#!/usr/bin/env python
"""
find data in old ADIOS DB with emulsifiation constant
"""

datafile = "../data/OilLib.txt"


with (open(datafile, encoding='latin-1') as infile,
      open("Emulsion_data_adios2.tsv", 'w') as outfile):
    outfile.write("ID\tName\tWater_content\tBullwinkle_max,Bullwinkle_min\n")
    infile.readline()

    header = infile.readline().split("\t")
    header_map = {name.strip(): idx for idx, name in enumerate(header)}

    for rec in infile:
        rec = rec.split("\t")
        num_rec = []

        for f in rec:
            try:
                num_rec.append(float(f))
            except ValueError:
                num_rec.append(f)

        rec = num_rec
        ID = rec[header_map['ADIOS_Oil_ID']]
        name = rec[header_map['Oil_Name']]
        water_cont = rec[header_map['Water_Content_Emulsion']]
        bull_min = rec[header_map['Emuls_Constant_Min']]
        bull_max = rec[header_map['Emuls_Constant_Max']]

        if water_cont or bull_max or bull_min:
            print(ID, water_cont, bull_max, bull_min)
            outfile.write(f"{ID} \t{name:50s}\t{water_cont:6}\t{bull_max:6}\t{bull_min:6}\n")
