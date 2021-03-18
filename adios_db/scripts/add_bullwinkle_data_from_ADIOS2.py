#!/usr/bin/env python

"""
find data in old ADIOS DB with emulsifiation constant

"""

from pathlib import Path
import math
import adios_db.scripting as ads



adios_data = Path("../data/OilLib.txt")
json_data_dir = Path("../../../noaa-oil-data/data/oil/AD/")


def process(adios_data, json_data_dir):
    # Read the data
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
    # delete any extra subsamples
    del oil.sub_samples[1:]
    # delete any emulsion already in the fresh subsample
    del oil.sub_samples[0].environmental_behavior.emulsions[:]

    if bull_max < bull_min:
        raise ValueError("Bullwinkle minimum should be less than the maximum")

    if water_cont:
        if (bull_min == '') or (bull_min == 0):
            add_emulsion_to_fresh_subsample(oil, water_cont)
        elif bull_min < bull_max:
            # add one with zero water content.
            add_emulsion_subsample(oil, bull_min, 0.0)
        if bull_max != '':
            add_emulsion_subsample(oil, bull_max, water_cont)
    else:
        pass
        # # we have all the data
        # if math.isclose(bull_max, bull_min):  # One value, one subsample

        #     assert False

def add_emulsion_to_fresh_subsample(oil, water_cont):
    print("Adding Emulsion Data to Fresh Oil")
    fresh = oil.sub_samples[0]
    emul = ads.Emulsion(water_content=ads.MassFraction(value=water_cont,
                                                       unit="fraction"),
                        )
    fresh.environmental_behavior.emulsions.append = emul


def add_emulsion_subsample(oil, bull_min, water_cont):
    sample = ads.Sample()
    sample.metadata.name = "Weathered sample that did not form an emulsion"
    sample.metadata.short_name = "No emulsion fraction"
    sample.metadata.description = ("Partially weathered sample that did not form an emulsion.\n\n"
                                   "See record reference for details")
    sample.metadata.fraction_weathered = ads.MassFraction(value=bull_min,
                                                          unit="fraction",
                                                          )

    # create the Emulsion object
    emul = ads.Emulsion(water_content=ads.MassFraction(value=water_cont,
                                                       unit="fraction"),
                        )
    sample.environmental_behavior.emulsions.append(emul)
    oil.sub_samples.append(sample)



process(adios_data, json_data_dir)

