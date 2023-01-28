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
from adios_db.models.oil.metadata import MetaData
from adios_db.models.oil.product_type import ProductType
from adios_db.models.oil.values import Reference

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
                warnings.warn("Data model version mismatch -- possible errors on import")
            break
    # look for main metadata:
    for row in reader:
        if check_field_name(row[0], "Record Metadata"):
            break
    # read the metadata:
    oil.metadata = read_record_metadata(reader)

    return oil

def read_record_metadata(reader):
    """
    read the record metadata -- stops when "Subsample Metadata" is reached.

    returns a Metadata object
    """

    # reference: Reference = field(default_factory=Reference)
    # labels: list = field(default_factory=list)
    # alternate_names: list = field(default_factory=list)
    # location_coordinates: LocationCoordinates = None

    metadata_map = {
        normalize("Name"): ("name", str),
        normalize("Source ID"): ("source_id", str),
        normalize("Location"): ("location", str),
        normalize("Sample Date"): ("sample_date", str),
        normalize("Comments"): ("comments", str),
        normalize("API Gravity"): ("API", float),
        normalize("Product Type"): ("product_type", ProductType),
        # normalize("Product Type"): ("reference", Reference),
    }
    print("reading metadata")
    md = MetaData()
    # look for subsample data, then stop
    for row in reader:
        if check_field_name(row[0], "Subsample Metadata"):
            print("found subsample, breaking out")
            break
        else:
            print("reading metadata")
            # this could be more efficient with a dict lookup, rather than a loop
            # but would require normalization
            try:
                if row[1]:
                    attr, func = metadata_map[normalize(row[0])]
                    setattr(md, attr, func(row[1]))
            except KeyError:
                if check_field_name(row[0], "Reference"):
                    md.reference = Reference(int(row[1]), row[2])

    return md



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


if __name__ == "__main__":
    main()



