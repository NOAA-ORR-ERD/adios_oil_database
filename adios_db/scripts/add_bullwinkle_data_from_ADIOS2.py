#!/usr/bin/env python

"""
find data in old ADIOS DB with emulsifiation constant

"""

from pathlib import Path
import adios_db.scripting as ads



adios_data = Path("../data/OilLib.txt")
json_data_dir = Path("../../../noaa-oil-data/data/oil/AD/")


# Read the data
def process(adios_data, json_data_dir):
    with (open(adios_data, encoding='latin-1') as infile,
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
                print("making subsamples for:")
                print(ID, water_cont, bull_max, bull_min)
                outfile.write(f"{ID} \t{name:50s}\t{water_cont:6}\t{bull_max:6}\t{bull_min:6}\n")
                make_subsamples(ID, water_cont, bull_max, bull_min)


def make_subsamples(ID, water_cont, bull_max, bull_min):
    # get the record:
    path = json_data_dir / (ID + ".json")
    print(path)
    oil = ads.Oil.from_file(path)
    # Only water content
    # Add emulsion data to the fresh oil
    if water_cont and bull_max == '' and bull_min == '':
        print("just water content")
        fresh = oil.sub_samples[0]
        print(fresh)
        print(fresh.environmental_behavior.emulsions[0])
        if len(fresh.environmental_behavior.emulsions) > 1:
            raise ValueError("more than one emulsion")
        emul = ads.Emulsion(water_content=ads.MassFraction(value=water_cont,
                                                           unit="fraction"),
                            age=ads.Time(value=0.0, unit='day'))
        fresh.environmental_behavior.emulsions[0] = emul

        print(emul)
        raise Exception



process(adios_data, json_data_dir)

