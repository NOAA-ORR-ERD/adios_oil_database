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
import logging

import nucos

from adios_db.util import BufferedIterator
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
                                                     PourPoint,
                                                     FlashPoint,
                                                     )
from adios_db.models.oil.distillation import Distillation, DistCutList
from adios_db.models.oil.sara import Sara
from adios_db.models.oil.compound import Compound, CompoundList
from adios_db.models.oil.bulk_composition import BulkComposition, BulkCompositionList
from adios_db.models.oil.industry_property import IndustryProperty, IndustryPropertyList
from adios_db.models.oil.cleanup import FixAPI

from adios_db.models.common.measurement import MassFraction, Temperature, MassOrVolumeFraction, AnyUnit

import logging



def padded_csv_reader(file_path, num_fields=6):
    """
    a csv reader that pads the rows to always include the specified number of blank fields
    """
    with open(file_path, encoding="utf-8-sig") as infile:
        reader = csv.reader(infile, dialect='excel')
        for i, row in enumerate(reader):
            row += [""] * (num_fields - len(row))
            # this broke a lot -- which is odd, but ???
            # row = [f.strip() for f in row]
            logging.debug(f"Processing row: {i}: , {row}")
            yield row


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
        reader = BufferedIterator(padded_csv_reader(infilename))

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
        # oil.sub_samples.append(read_subsample(reader))

        # breakpoint()
        # Read the Samples
        for row in reader:
            if check_field_name(row[0], 'Subsample Metadata'):
                ss = read_subsample(reader)
                oil.sub_samples.append(ss)


        # add in API if it's not there:
        # note: maybe add a cleanup options?
        if not oil.metadata.API:
            FixAPI(oil).cleanup()

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
    logging.debug("reading record metadata")
    for row in reader:
        if check_field_name(row[0], "Subsample Metadata"):
            reader.push(row)
            logging.debug("found Subsample metadata, breaking out")
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
                    md.reference = Reference(int(row[1]), row[2].strip())
                if check_field_name(row[0], "Alternate Names"):
                    md.alternate_names = [n.strip() for n in row[1:] if n.strip()]
                if check_field_name(row[0], "Labels"):
                    md.labels = [n.strip() for n in row[1:] if n.strip()]

    return md


def read_subsample(reader):
    logging.debug("reading subsample")
    ss = Sample(metadata=read_subsample_metadata(reader))
    ss.physical_properties = read_physical_properties(reader)
    ss.distillation_data = read_distillation_data(reader)
    ss.SARA = read_sara(reader)
    ss.compounds = read_compounds(reader)
    ss.bulk_composition = read_bulk_composition(reader)
    ss.industry_properties = read_industry_properties(reader)
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
            logging.debug("found Physical Properties: breaking out")
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
    """
    logging.debug("Reading physical Properties")
    pp = PhysicalProperties()

    for row in reader:
        if check_field_name(row[0], "Distillation Data"):
            logging.debug('found "Distillation Data": breaking out')
            break
        else:
            if check_field_name(row[0], "Pour Point"):
                m = Temperature(**read_measurement(row[1:]))
                pp.pour_point = None if empty_measurement(m) else PourPoint(measurement=m)
            if check_field_name(row[0], "Flash Point"):
                m = Temperature(**read_measurement(row[1:]))
                pp.flash_point = None if empty_measurement(m) else  FlashPoint(measurement=m)
            if check_field_name(row[0], "Density"):
                pp.densities = read_densities(reader)
            if check_field_name(row[0], "Kinematic Viscosity"):
                pp.kinematic_viscosities = read_kvis(reader)
            if check_field_name(row[0], "Dynamic Viscosity"):
                pp.dynamic_viscosities = read_dvis(reader)

    return pp


def read_densities(reader):
    logging.debug("reading densities")
    data = []
    for row in reader:
        if (  check_field_name(row[0], "Density at temp")
              and "".join(row[1:]).strip()):
            data.append(read_val_at_temp_row(row[1:]))
        else:
            break
    logging.debug(f"density data: {data}")
    return DensityList.from_data(data)


def read_kvis(reader):
    logging.debug("reading kinematic viscosities")
    data = []
    for row in reader:
        if (check_field_name(row[0], "Viscosity at temp")
              and "".join(row[1:]).strip()):
            data.append(read_val_at_temp_row(row[1:]))
        else:
            break
        logging.debug(f"kvis data: {data}")
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
    sara_names = {n:i for n, i in zip(("saturates", "aromatics", "resins", "asphaltenes"), range(4))}
    sara_data = [None] * 4
    unit = None
    method = None
    for row in reader:
        if check_field_name(row[0], "Compounds"):
            logging.debug('found "Compounds": breaking out')
            break
        else:
            name = row[0].strip().lower()
            if name == "method":
                m = row[1].strip()
                method = m if m else None
            elif name in sara_names:
                data = read_val_and_unit(row[1:])
                if data is not None:
                    if unit is not None:
                        if unit != data["unit"]:

                            raise ValueError("units must be consistent in SARA data:"
                                             f"{unit} and {data.unit()}")
                    else:
                        unit = data['unit']
                    sara_data[sara_names[name]] = data['value']
    sara = Sara.from_data(sara_data, unit)
    sara.method = method

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
            logging.debug('found "Bulk Composition": breaking out')
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
        if check_field_name(row[0], "Industry Properties"):
            logging.debug('found "Industry Properties": breaking out')
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


def read_industry_properties_row(row):
    """
    reads  the compound data
    Name,  fraction,  Fraction Unit, unit type, method,  comment, groups
    """
    name = row[0].strip()
    if not name:
        "no name, returning"
        return None
    value = float_or_placeholder(row[1])
    if value is None:
        # not value, returning
        return None
    unit = row[2].strip()
    unit_type = row[3].strip()
    method = row[4].strip()
    return IndustryProperty(name=name,
                            measurement=AnyUnit(value=value, unit=unit, unit_type=unit_type),
                            method=method,
                            )


def read_industry_properties(reader):
    ind_props = IndustryPropertyList()
    for row in reader:
        if check_field_name(row[0], "Subsample Metadata"):
            reader.push(row)
            logging.debug('found "Subsample Metadata": breaking out')
            break
        else:
            first = row[0].strip().lower()
            if not first.startswith('property'):
                # done with compounds -- or blank line?
                continue
            ind_prop = read_industry_properties_row(row[1:])
            if ind_prop is not None:
                ind_props.append(ind_prop)

    return ind_props


def read_distillation_data(reader):
    try:
        dist_data = Distillation()
        for row in reader:
            if check_field_name(row[0], "SARA Analysis"):
                logging.debug('found "SARA Analysis": breaking out')
                break
            else:
                if row[0].strip().lower().startswith("type"):
                    dist_data.type = row[1].strip()
                elif check_field_name(row[0], "Method"):
                    dist_data.method = row[1].strip()
                elif check_field_name(row[0], "Final Boiling Point"):
                    data = read_val_and_unit(row[1:])
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
    except: # bare except because it's going to re-raise
        print("*** Error reading Distillation data. Last row read:")
        print(row)
        raise

    return dist_data


def read_dist_cut_table(reader, unit_type):
    logging.debug("reading distillation cuts")

    fractions = []
    temps = []
    frac_unit = None
    temp_unit = None
    try:
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
    except:  # bare except, because it re-raises
        print("*** Error reading distillation cuts: last row read:")
        print(row)
        raise
    logging.debug(f"Distillation Data: {[(frac, temp) for frac, temp in zip(fractions, temps)]}")

    try:
        DCL = DistCutList.from_data_arrays(fractions,
                                           temps,
                                           frac_unit,
                                           temp_unit,
                                           unit_type=unit_type)
    except nucos.InvalidUnitTypeError:
        print('*** Error: Distillation type must be "Mass Fraction" or "Volume Fraction"')
        raise
    return DCL


def float_or_placeholder(val):
    """
    convert a string to a float

    return None if empty, or a placeholder value: e.g. min_value

    raise an exception is not a known placeholder, and not a float
    """
    placeholders = ['value', 'fraction', 'temp']
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


def empty_measurement(meas):
    """
    is a measurement empty?
    """
    for v in (meas.min_value, meas.value, meas.max_value):
        if v is not None:
            return False
    return True


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
    return "".join(name.split()).lower().rstrip(':')


def check_field_name(field, name):
    # this somehow broke a few things
    # return normalize(name).startswith(normalize(field))
    return normalize(field) == normalize(name)


# Utilities:
def strstrip(obj):
    return str(obj).strip()

