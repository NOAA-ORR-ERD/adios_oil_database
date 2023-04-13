#!/usr/bin/env python

"""
Script to import data from a CSV file exported from the
NOAA "standard" Excel template.

That template should be in this repo in the "data" folder

Note that the CSV should be exported as "CSV utf-8 Comma Delimited"
"""
import csv
from pathlib import Path
import sys
import warnings

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.version import Version
from adios_db.models.oil.metadata import MetaData, SampleMetaData
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.product_type import ProductType
from adios_db.models.oil.values import Reference
from adios_db.models.oil.physical_properties import PhysicalProperties
from adios_db.models.common.measurement import MassFraction, Temperature


def read_csv_file(infilename):
    """
    Read the CSV file infilename

    Return an Oil object
    """
    infile = open(infilename, encoding="utf-8-sig")
    reader = csv.reader(infile, dialect='excel')
    oil = Oil('XXXXXX')

    # look for the Data model version
    # this will skip any extra stuff before that
    for row in reader:
        if check_field_name(row[0], "ADIOS Data Model Version"):
            if Version(row[1]) != oil.adios_data_model_version:
                warnings.warn('Data model version mismatch '
                              '-- possible errors on import')
            break

    # look for main metadata:
    for row in reader:
        if check_field_name(row[0], "Record Metadata"):
            break

    # read the metadata:
    oil.metadata = read_record_metadata(reader)

    # load the subsamples:
    while True:
        oil.sub_samples.append(read_subsample(reader))
        break

    return oil


def read_record_metadata(reader):
    """
    read the record metadata -- stops when "Subsample Metadata" is reached.

    returns a Metadata object
    """
    # reference: Reference = field(default_factory=Reference)
    # location_coordinates: LocationCoordinates = None

    md = MetaData()
    metadata_map = {
        normalize("Name"): ("name", strstrip),
        normalize("Source ID"): ("source_id", strstrip),
        normalize("Location"): ("location", strstrip),
        normalize("Sample Date"): ("sample_date", strstrip),
        normalize("Comments"): ("comments", strstrip),
        normalize("API Gravity"): ("API", float),
        normalize("Product Type"): ("product_type", ProductType),
        # normalize("Product Type"): ("reference", Reference),
    }

    # look for subsample data, then stop
    for row in reader:
        if check_field_name(row[0], "Subsample Metadata"):
            break
        else:
            # This could be more efficient with a dict lookup rather than a
            # loop, but would require normalization
            try:
                if row[1]:
                    attr, func = metadata_map[normalize(row[0])]
                    setattr(md, attr, func(row[1]))
            except KeyError:
                if check_field_name(row[0], "Reference"):
                    md.reference = Reference(int(row[1]), row[2])

                if check_field_name(row[0], "Alternate Names"):
                    md.alternate_names = [n.strip()
                                          for n in row[1:]
                                          if n.strip()]

                if check_field_name(row[0], "Labels"):
                    md.labels = [n.strip() for n in row[1:] if n.strip()]

    return md


def read_subsample(reader):
    ss = Sample(metadata=read_subsample_metadata(reader))
    ss.physical_properties = read_physical_properties(reader)

    return ss


def read_subsample_metadata(reader):
    """
    Read the record metadata -- stops when "Physical Properties" is reached.

    returns a SubsampleMetadata object

    class SampleMetaData:
    name: str = "Fresh Oil Sample"
    short_name: str = None
    sample_id: str = None
    description: str = None
    fraction_evaporated: MassFraction = None
    boiling_point_range: Temperature = None
    """
    # reference: Reference = field(default_factory=Reference)
    # location_coordinates: LocationCoordinates = None

    md = SampleMetaData()
    metadata_map = {
        normalize("Name"): ("name", strstrip),
        normalize("Short name"): ("short_name", strstrip),
        normalize("Sample ID"): ("sample_id", strstrip),
        normalize("Description"): ("description", strstrip),
    }

    # look for Physical Properties data, then stop
    for row in reader:
        print("Processing:", row)
        if check_field_name(row[0], "Physical Properties"):
            # print("found Physical Properties: breaking out")
            break
        else:
            # this could be more efficient with a dict lookup rather than a
            # loop, but would require normalization
            try:
                if row[1]:
                    attr, func = metadata_map[normalize(row[0])]
                    setattr(md, attr, func(row[1]))
            except KeyError:
                if check_field_name(row[0], "Fraction evaporated"):
                    md.fraction_evaporated = MassFraction(
                        value=float(row[2]),
                        unit=strstrip(row[3])
                    )

                if check_field_name(row[0], "Boiling Point Range"):
                    md.boiling_point_range = Temperature(
                        min_value=float(row[1]),
                        max_value=float(row[2]),
                        unit=strstrip(row[3])
                    )

    return md


def read_physical_properties(reader):
    """
    read the physical properties data

    Stops when "Distillation Data" is reached

    class PhysicalProperties:
    """
    pp = PhysicalProperties()
    # pp_map = {
    #     normalize("Name"): ("name", strstrip),
    #     normalize("Short name"): ("short_name", strstrip),
    #     normalize("Sample ID"): ("sample_id", strstrip),
    #     normalize("Description"): ("description", strstrip),
    # }

    # look for "Distillation Data" data, then stop
    for row in reader:
        print("Processing:", row)
        if check_field_name(row[0], "Distillation Data"):
            print('found "Distillation Data": breaking out')
            break
        else:
            pass
            # # this could be more efficient with a dict lookup rather than a
            # # loop, but would require normalization
            # try:
            #     if row[1]:
            #         attr, func = metadata_map[normalize(row[0])]
            #         setattr(md, attr, func(row[1]))
            # except KeyError:

            if check_field_name(row[0], "Pour Point"):
                pp.pour_point = Temperature(**read_measurement(row[1:]))

            if check_field_name(row[0], "Flash Point"):
                pp.flash_point = Temperature(**read_measurement(row[1:]))

    return pp


def read_measurement(items):
    """
    reads a sequence, and returns a dict of measurement values:

    min_value=float(row[1]),
    value=float(row[2]),
    max_value=float(row[3]),
    unit
    """
    vals = {}
    for key, val in zip(('min_value', 'value', 'max_value'), items[:3]):
        vals[key] = float(val) if val.strip() else None

    vals['unit'] = strstrip(items[3])

    return vals


def normalize(name):
    """
    normalizes a name:
      removes whitespace
      lower cases it
    """
    return "".join(name.split()).lower()


def check_field_name(field, name):
    return normalize(field) == normalize(name)


def main():
    """
    Read the data the CSV file provided on the command line

    export it as a JSON file
    """
    try:
        infilename = Path(sys.argv[1])
    except IndexError:
        print("You must provide the filename on the command line")
        sys.exit()

    try:
        outfilename = Path(sys.argv[2])
    except IndexError:
        outfilename = infilename.with_suffix(".json")

    print("Reading:", infilename)
    oil = read_csv_file(infilename)
    print(f"Saving: {outfilename} as JSON")
    oil.to_file(outfilename)


def strstrip(obj):
    return str(obj).strip()


if __name__ == "__main__":
    main()
