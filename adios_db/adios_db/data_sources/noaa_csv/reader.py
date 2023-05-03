"""
module for reading the "standard CSV format"

Generated from the Excel Template:

adios_db/data/ADIOS_data_template.xlsx

Note that the CSV should be exported as "CSV utf-8 Comma Delimited"
"""

import csv

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
from adios_db.models.oil.physical_properties import (PhysicalProperties,
                                                     DensityList,
                                                     )
from adios_db.models.common.measurement import MassFraction, Temperature



def read_csv(filename, oil_id="PlaceHolder"):
    reader = Reader(oil_id)
    reader.load_from_csv(filename)

    return reader.oil


class Reader():
    def __init__(self, oil_id):
        self.oil = Oil(oil_id)

    def load_from_csv(self, infilename):
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
        # load the subsamples:
        while True:
            print("about the read the sub_samples")
            oil.sub_samples.append(read_subsample(reader))
            break

        self.oil = oil

def read_record_metadata(reader):
    """
    read the record metadata -- stops when "Subsample Metadata" is reached.

    returns a Metadata object
    """

    # reference: Reference = field(default_factory=Reference)
    # location_coordinates: LocationCoordinates = None

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
    md = MetaData()
    # look for subsample data, then stop
    for row in reader:
        if check_field_name(row[0], "Subsample Metadata"):
            break
        else:
            # this could be more efficient with a dict lookup, rather than a loop
            # but would require normalization
            try:
                if row[1]:
                    attr, func = metadata_map[normalize(row[0])]
                    setattr(md, attr, func(row[1]))
            except KeyError:
                if check_field_name(row[0], "Reference"):
                    md.reference = Reference(int(row[1]), row[2])
                if check_field_name(row[0], "Alternate Names"):
                    md.alternate_names = [n.strip() for n in row[1:] if n.strip()]
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

    metadata_map = {
        normalize("Name"): ("name", strstrip),
        normalize("Short name"): ("short_name", strstrip),
        normalize("Sample ID"): ("sample_id", strstrip),
        normalize("Description"): ("description", strstrip),
    }
    md = SampleMetaData()
    # look for Physical Properties data, then stop
    for row in reader:
        print("Processing:", row)
        if check_field_name(row[0], "Physical Properties"):
            # print("found Physical Properties: breaking out")
            break
        else:
            # this could be more efficient with a dict lookup, rather than a loop
            # but would require normalization
            try:
                if row[1]:
                    attr, func = metadata_map[normalize(row[0])]
                    setattr(md, attr, func(row[1]))
            except KeyError:
                if check_field_name(row[0], "Fraction evaporated"):
                    md.fraction_evaporated = MassFraction(value=float(row[2]),
                                                          unit=strstrip(row[3]))
                if check_field_name(row[0], "Boiling Point Range"):
                    md.boiling_point_range = Temperature(min_value=float(row[1]),
                                                         max_value=float(row[2]),
                                                         unit=strstrip(row[3]))
    return md

def read_physical_properties(reader):
    """
    read the physical properties data

    Stops when "Distillation Data" is reached

    class PhysicalProperties:

    pour_point: PourPoint = None
    flash_point: FlashPoint = None

    densities: DensityList = field(default_factory=DensityList)
    kinematic_viscosities: KinematicViscosityList = field(default_factory=KinematicViscosityList)
    dynamic_viscosities: DynamicViscosityList = field(default_factory=DynamicViscosityList)

    interfacial_tension_air: InterfacialTensionList = field(default_factory=InterfacialTensionList)
    interfacial_tension_water: InterfacialTensionList = field(default_factory=InterfacialTensionList)
    interfacial_tension_seawater: InterfacialTensionList = field(default_factory=InterfacialTensionList)
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
            # # this could be more efficient with a dict lookup, rather than a loop
            # # but would require normalization
            # try:
            #     if row[1]:
            #         attr, func = metadata_map[normalize(row[0])]
            #         setattr(md, attr, func(row[1]))
            # except KeyError:

            if check_field_name(row[0], "Pour Point"):
                pp.pour_point = Temperature(**read_measurement(row[1:]))
            if check_field_name(row[0], "Flash Point"):
                pp.flash_point = Temperature(**read_measurement(row[1:]))
            if check_field_name(row[0], "Density"):
                pp.densities = read_densities(reader)

    return pp

def read_densities(reader):
    densities = DensityList
    for row in reader:
        if check_field_name(row[0], "Pour Point"):
            pass


def read_measurement(items):
    """
    reads a sequence, and returns a dict of measurement values:

    min_value=float(row[1]),
    value=float(row[2]),
    max_value=float(row[3]),
    unit
    """
    vals = {}
    for key, val in zip(('min_value', 'value', 'max_value' ), items[:3]):
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


# Utilities:
def strstrip(obj):
    return str(obj).strip()

########
##
## Old code 0 accidentally duplicated it :-(
##
## Delete if it's not useful in the end
########
#     def load_from_csv(self, infile):
#         with open(infile, newline='') as csvfile:
#             self.reader = reader = csv.reader(csvfile, delimiter=',')

#             header = next(reader)
#             if header[0].lower() == "ADIOS Data Model Version".lower():
#                 data_model_version = Version(header[1])
#             else:
#                 raise ValueError("First line doesn't match "
#                                  "-- are you sure this is a standard "
#                                  "ADIOS CSV file?\n"
#                                  f"First line of file: {header}")

#             if data_model_version > ADIOS_DATA_MODEL_VERSION:
#                 raise ValueError("Version mismatch -- this file is: "
#                                  f"{data_model_version}\n"
#                                  "The code version is: "
#                                  f"{ADIOS_DATA_MODEL_VERSION}")

#             self.oil = Oil("Placeholder")

#             # metadata
#             line = next_non_empty(reader)
#             if line[0].lower() != "Record Metadata".lower():
#                 raise ValueError("Next section should be Record Metadata")

#             for line in reader:
#                 if line[0].lower().strip() == "subsample metadata":
#                     print("reached subsample, breaking")
#                     break
#                 else:
#                     self.read_record_metadata(line)

#     def read_record_metadata(self, line):
#         line = [f.strip() for f in line]
#         field = line[0].lower().strip()
#         value = line[1].strip()

#         print("reading metadata line")
#         print(line)
#         print(f"{field=}, {value=}")

#         if field == "name":
#             self.oil.metadata.name = value
#         elif field == "api gravity":
#             self.oil.metadata.API = round(float(value), 2)
#         elif field == 'source id':
#             self.oil.metadata.source_id = value
#         elif field == 'alternate names':
#             for name in line[1:]:
#                 if name:
#                     self.oil.metadata.alternate_names.append(name)
#         elif field == 'location':
#             self.oil.metadata.location = value
#         elif field == 'reference':
#             try:
#                 year = int(value)
#                 print(year)

#                 if not(1900 < year < 2100):
#                     raise ValueError("year not in bounds")
#                 self.oil.metadata.reference.year = int(value)
#             except ValueError:
#                 raise

#             if line[2]:
#                 self.oil.metadata.reference.reference = line[2].strip()


# def next_non_empty(reader):
#     """
#     returns the next line that has nothing in the first field
#     """
#     while True:
#         line = next(reader)
#         if line[0]:
#             return line
