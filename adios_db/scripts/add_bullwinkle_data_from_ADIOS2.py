#!/usr/bin/env python
"""
find data in old ADIOS DB with emulsifiation constant
"""
import sys
from pathlib import Path
import math
import adios_db.scripting as ads


adios_data = Path("../data/OilLib.txt")
json_data_dir = Path("../../../noaa-oil-data/data/oil/AD/")


def process(adios_data, json_data_dir):
    # Read the data
    with (open(adios_data, encoding='latin-1') as infile,
          open("Emulsion_data_adios2.tsv", 'w') as outfile):
        # outfile.write("ID\tName\tWater_content\tBullwinkle_max,Bullwinkle_min\n")
        outfile.write(f'{"ID":8} \t{"Name":50s}\t{"WaterCont":6}\t{"Max":6}\t{"Min":6}\n')
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
            refrence = rec[header_map['Reference']]

            if water_cont or bull_max or bull_min:
                print("\nMaking subsamples for:")
                print(name)
                print(f"{ID=}, {water_cont=}, {bull_max=}, {bull_min=}")
                outfile.write(f"{ID} \t{name:50s}\t{water_cont:6}\t{bull_max:6}\t{bull_min:6}\t {refrence}\n")
                make_subsamples(ID, water_cont, bull_max, bull_min)


def make_subsamples(ID, water_cont, bull_max, bull_min):
    # get the record:
    path = json_data_dir / (ID + ".json")
    oil = ads.Oil.from_file(path)

    # Only water content
    # Add emulsion data to the fresh oil
    # delete any emulsions in all subsamples
    for sub in oil.sub_samples:
        del sub.environmental_behavior.emulsions[:]

    if bull_max < bull_min:
        raise ValueError("Bullwinkle minimum should be less than the maximum")

    processed = False
    if water_cont:
        if (bull_min == '') or (bull_min == 0.0):
            add_emulsion_to_fresh_subsample(oil, water_cont)
            processed = True
        elif bull_min < bull_max:
            # add one with zero water content.
            add_emulsion_subsample(oil, bull_min, 0.0)
            processed = True

        if bull_max != '' and bull_max > 0.0:
            add_emulsion_subsample(oil, bull_max, water_cont)
            processed = True

        if bull_min == '' and bull_max == '':
            print("adding warning")
            oil.permanent_warnings.append(
                "Warning: ADIOS2 data had a value for water content, "
                "but min and max emulsification constant were blank. "
                "0.0 has been assumed, but that may not  be correct"
            )
    else:
        if bull_min == '' or bull_max == '':
            raise Exception("min or max is empty")

        if bull_min < bull_max:
            add_emulsion_subsample(oil, bull_min, 0.0)
            processed = True

        if bull_min == bull_max:
            add_emulsion_subsample_unknown_wc(oil, bull_max)
            processed = True

    if processed:
        if dry_run:
            print("Nothing saved")
        else:
            print("writing to file")
            oil.to_file(path)
    else:
        raise Exception("Nothing done to this record -- something went wrong.")


def add_emulsion_to_fresh_subsample(oil, water_cont):
    print(f"Adding Emulsion Data to Fresh Oil: {water_cont=}")
    fresh = oil.sub_samples[0]
    emul = ads.Emulsion(water_content=ads.MassFraction(value=water_cont,
                                                       unit="fraction"))
    fresh.environmental_behavior.emulsions.append(emul)


def add_emulsion_subsample(oil, bull, water_cont):
    print(f"Adding Emulsion Subsample: {bull=}, {water_cont=}")
    # is there one already there?
    for s in oil.sub_samples[1:]:
        if s.metadata.fraction_weathered.value == bull:
            print("found an existing Subsample, using that")
            sample = s
            break
    else:
        sample = ads.Sample()
        oil.sub_samples.append(sample)

    if water_cont == 0:
        sample.metadata.name = "Weathered sample that did not form an emulsion"
        sample.metadata.short_name = "Didn't Emulsify"
        sample.metadata.description = ("Partially weathered sample that "
                                       "did not form an emulsion.\n\n"
                                       "See record reference for details")
    else:
        sample.metadata.name = "Weathered sample that formed an emulsion"
        sample.metadata.short_name = "Emulsified"
        sample.metadata.description = ("Partially weathered sample that "
                                       "formed an emulsion.\n\n"
                                       "See record reference for details")

    sample.metadata.fraction_weathered = ads.MassFraction(value=bull,
                                                          unit="fraction")

    # create the Emulsion object
    emul = ads.Emulsion(water_content=ads.MassFraction(value=water_cont,
                                                       unit="fraction"))
    sample.environmental_behavior.emulsions.append(emul)


def add_emulsion_subsample_unknown_wc(oil, bull):
    print(f"Adding Emulsion Subsample with no water content: {bull=}")

    # is there one already there?
    for s in oil.sub_samples[1:]:
        if s.metadata.fraction_weathered.value == bull:
            print("found an existing Subsample, using that")
            sample = s
            break
    else:
        sample = ads.Sample()
        oil.sub_samples.append(sample)

    sample.metadata.name = "Weathered sample that formed an emulsion"
    sample.metadata.short_name = "Emulsified"
    sample.metadata.description = ("Partially weathered sample that "
                                   "formed an emulsion of unknown "
                                   "water content.\n\n"
                                   "See record reference for details")
    sample.metadata.fraction_weathered = ads.MassFraction(value=bull,
                                                          unit="fraction")

    # create the Emulsion object
    emul = ads.Emulsion(water_content=ads.MassFraction(min_value=0.0,
                                                       unit="fraction"))
    sample.environmental_behavior.emulsions.append(emul)


if __name__ == "__main__":
    if "dry_run" in sys.argv:
        dry_run = True
    else:
        dry_run = False

    process(adios_data, json_data_dir)
