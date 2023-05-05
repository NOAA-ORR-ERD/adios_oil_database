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
                                                     KinematicViscosityList,
                                                     DynamicViscosityList,
                                                     )
from adios_db.models.oil.distillation import Distillation, DistCutList
from adios_db.models.oil.sara import Sara
from adios_db.models.oil.compound import Compound, CompoundList
from adios_db.models.oil.bulk_composition import BulkComposition, BulkCompositionList

from adios_db.models.common.measurement import MassFraction, Temperature, MassOrVolumeFraction


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
                    warnings.warn("Data model version mismatch -- possible errors on import\n"
                                  f"Version in file: {row[1]}\n"
                                  f"Version in code: {oil.adios_data_model_version}\n"
                                  )
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
    ss.distillation_data = read_distillation_data(reader)
    ss.SARA = read_sara(reader)
    ss.compounds = read_compounds(reader)
    ss.bulk_composition = read_bulk_composition(reader)

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
                    try:
                        md.boiling_point_range = Temperature(min_value=float(row[1]),
                                                             max_value=float(row[2]),
                                                             unit=strstrip(row[3]))
                    except ValueError:
                        # to catch "min_value"
                        # this could mask other errors, but for now
                        pass
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
            if check_field_name(row[0], "Kinematic Viscosity"):
                pp.kinematic_viscosities = read_kvis(reader)
            if check_field_name(row[0], "Dynamic Viscosity"):
                pp.dynamic_viscosities = read_dvis(reader)

    return pp

def read_densities(reader):
    data = []
    for row in reader:
        if (  check_field_name(row[0], "Density at temp")
              and "".join(row[1:]).strip()):
            data.append(read_val_at_temp_row(row[1:]))
        else:
            break

    return DensityList.from_data(data)

def read_kvis(reader):
    data = []
    for row in reader:
        if (  check_field_name(row[0], "Viscosity at temp")
              and "".join(row[1:]).strip()):
            data.append(read_val_at_temp_row(row[1:]))
        else:
            break
    return KinematicViscosityList.from_data(data)


def read_dvis(reader):
    data = []
    for row in reader:
        if (  check_field_name(row[0], "Viscosity at temp")
              and "".join(row[1:]).strip()):
            data.append(read_val_at_temp_row(row[1:]))
        else:
            break
    return DynamicViscosityList.from_data(data)


def read_sara(reader):
    sara = Sara()
    sara_names = {"saturates", "aromatics", "resins", "asphaltenes"}
    for row in reader:
        if check_field_name(row[0], "Compounds"):
            print('found "Compounds": breaking out')
            break
        else:
            name = row[0].strip().lower()
            if name in sara_names:
                setattr(sara, name, read_val_and_unit(row[1:]))
            elif name == "method":
                m = row[1].strip()
                sara.method = m if m else None
    return sara


def read_compound(row):
    """
    reads  the compound data
    name, fraction, frac_unit, method, comment, groups = read_compound(row)
    """
    name = row[0].strip()
    if not name:
        return None
    fraction = float_or_placeholder(row[1])
    frac_unit = row[2].strip()
    method = row[3].strip()
    comment = row[4].strip()
    groups = [group for group in row[5:] if group.strip()]
    return Compound(name=name,
                    measurement=MassFraction(fraction, unit=frac_unit),
                    method=method,
                    comment=comment,
                    groups=groups
                    )


def read_compounds(reader):
    compounds = CompoundList()
    for row in reader:
        if check_field_name(row[0], "Bulk Composition"):
            print('found "Bulk Composition": breaking out')
            break
        else:
            first = row[0].strip().lower()
            if not first.startswith('compound'):
                # done with compounds -- or blank line?
                continue
            compound = read_compound(row[1:])
            if compound is not None:
                compounds.append(compound)

    return compounds


def read_bulk_composition_row(row):
    """
    reads  the compound data
    Name,  fraction,  Fraction Unit, unit type, method,  comment, groups
    """
    name = row[0].strip()
    if not name:
        "no name, returning"
        return None
    fraction = float_or_placeholder(row[1])
    frac_unit = row[2].strip()
    unit_type = row[3].strip()
    method = row[4].strip()
    comment = row[5].strip()
    groups = [group for group in row[6:] if group.strip()]
    return BulkComposition(name=name,
                    measurement=MassOrVolumeFraction(fraction, unit=frac_unit, unit_type=unit_type),
                    method=method,
                    comment=comment,
                    groups=groups
                    )

def read_bulk_composition(reader):
    bulk_comps = BulkCompositionList()
    for row in reader:
        print("Processing:", row)
        if check_field_name(row[0], "Industry Properties"):
            print('found "Industry Properties": breaking out')
            break
        else:
            first = row[0].strip().lower()
            if not first.startswith('composition'):
                # done with compounds -- or blank line?
                continue
            bulk_comp = read_bulk_composition_row(row[1:])
            if bulk_comp is not None:
                bulk_comps.append(bulk_comp)

    return bulk_comps


def read_distillation_data(reader):
    dist_data = Distillation()
    for row in reader:
        if check_field_name(row[0], "SARA Analysis"):
            print('found "SARA Analysis": breaking out')
            break
        else:
            if row[0].strip().lower().startswith("type"):
                dist_data.type = row[1].strip()
            elif check_field_name(row[0], "Method"):
                dist_data.method = row[1].strip()
            elif check_field_name(row[0], "Final Boiling Point"):
                data = read_val_and_unit(row[0])
                dist_data.end_point = Temperature(**data) if data is not None else None
            elif check_field_name(row[0], "Fraction Recovered"):
                data = read_val_and_unit(row[1:])
                if data is not None:
                    data['unit_type'] = dist_data.type
                    dist_data.fraction_recovered = MassOrVolumeFraction(**data) if data is not None else None
            elif check_field_name(row[0], "Distillation cuts"):
                cuts = read_dist_cut_table(reader, unit_type=dist_data.type)
                if cuts:
                    dist_data.cuts = cuts

    return dist_data


def read_dist_cut_table(reader, unit_type):
    fractions = []
    temps = []
    frac_unit = None
    temp_unit = None
    for row in reader:
        if not row[0].strip().lower().startswith('cut'):
            break
        frac, frac_u, temp, temp_u = read_val_at_temp_row(row[1:])
        if frac is None or temp is None:
            continue
        if frac_unit is None:
            frac_unit = frac_u
        elif frac_u != frac_unit:
            raise ValueError("fraction unit in distillation cuts should all be the same")
        if temp_unit is None:
            temp_unit = temp_u
        elif temp_u != temp_unit:
            raise ValueError("temperature unit in distillation cuts should all be the same")
        fractions.append(frac)
        temps.append(temp)

    return DistCutList.from_data_arrays(fractions,
                                        temps,
                                        frac_unit,
                                        temp_unit,
                                        unit_type=unit_type)


def float_or_placeholder(val):
    """
    convert a string to a float

    return None if empty, or a placeholder value: e.g. min_value

    raise an exception is not a known placeholder, and not a float
    """
    placeholders = ['value', 'fraction']
    if not val.strip():
        return None
    for placeholder in placeholders:
        if placeholder in val:
            return None
    else:
        try:
            return float(val)
        except ValueError:
            raise ValueError(f"{val} is not a valid number")


def read_val_and_unit(row):
    """
    reads a sequence, and returns a dict of measurement values:

    (used for density, viscosity, etc)

    returns: a sequence in proper types

    [value, value_unit, temp, temp_unit]

    """
    val = float_or_placeholder(row[0])
    if val is not None:
        vals = {'value': val,
                'unit': strstrip(row[1])}
        return vals
    else:
        return None


def read_val_at_temp_row(row):
    """
    reads a sequence, and returns a dict of measurement values:

    (used for density, viscosity, etc)

    returns: a sequence in proper types

    [value, value_unit, temp, temp_unit]

    """
    return [float_or_placeholder(row[0]), row[1].strip(), float_or_placeholder(row[2]), row[3].strip()]


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
       vals[key] = float_or_placeholder(val)
    vals['unit'] = strstrip(items[3])

    return vals


def read_min_max_unit(row):
    """
    read a minimum, maximum unit row

    assumes the field name is first item -- so ignores
    """
    data = {}
    try:
        data['min_value'] = float(row[1])
    except ValuError:
        if not "value" in row[1]:
            raise
    try:
        data['max_value'] = float(row[2])
    except ValuError:
        if not "value" in row[2]:
            raise
    data['unit'] = row[2].strip()

    return data


def normalize(name):
    """
    normalizes a name:
      removes whitespace
      lower cases it
    """
    return "".join(name.split()).lower()


def check_field_name(field, name):
    # this somehow broke a few things
    # return normalize(name).startswith(normalize(field))
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
