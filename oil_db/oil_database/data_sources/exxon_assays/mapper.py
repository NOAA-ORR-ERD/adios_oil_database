#!/usr/bin/env python
"""
Exxon Mapper

Not really a class -- it's really a function that build up an
oil object
"""
import re
import logging

import unit_conversion as uc

from oil_database.util import sigfigs
from oil_database.models.common.measurement import (UnittedValue,
                                                    Length,
                                                    Temperature,
                                                    MassFraction,
                                                    VolumeFraction,
                                                    Density,
                                                    KinematicViscosity,
                                                    Pressure)

from oil_database.models.oil.physical_properties import (DensityPoint,
                                                         KinematicViscosityPoint,
                                                         )
from oil_database.models.oil.properties import DistCut
from oil_database.models.oil.values import Reference

from oil_database.models.oil.oil import Oil
from oil_database.models.oil.sample import Sample, SampleList

from oil_database.models.oil.metadata import SampleMetaData
from oil_database.models.oil.compound import Compound
from oil_database.models.oil.physical_properties import PhysicalProperties
from oil_database.models.oil.environmental_behavior import EnvironmentalBehavior
from oil_database.models.oil.sara import Sara

logger = logging.getLogger(__name__)


def next_id():
    '''
        Generate the next oil record identifier
    '''
    if not hasattr(next_id, 'count'):
        next_id.count = 0
    next_id.count += 1

    return next_id.count


def norm(string):
    """
    normalizes a string for comparing

    so far: lower case, whitespace strip
    trailing and leading comma strip
    """
    return string.strip().strip(',').lower()


MAPPING = {
    norm('Cut volume, %'): {
        'attr': 'cut_volume',
        'unit': '%',
        'cls': VolumeFraction,
        'num_digits': 6,
    },
    #
    # API gravity,  # not a simple map
    #
    #
    # Specific Gravity (60/60F),
    #
    norm('Carbon, wt %'): {
        'attr': 'Carbon Mass Fraction',
        'unit': '%',
        'cls': MassFraction,
        'num_digits': 4,
        'element_of': 'bulk_composition',
    },
    norm('Hydrogen, wt %'): {
        'attr': 'Hydrogen Mass Fraction',
        'unit': '%',
        'cls': MassFraction,
        'num_digits': 4,
        'element_of': 'bulk_composition',
    },
    norm('Pour point, F'): {
        'attr': 'physical_properties.pour_point.measurement',
        'unit': 'C',
        'cls': Temperature,
        'num_digits': 8,
        'convert_from': 'F',
    },
    norm('Neutralization number (TAN), MG/GM'): {
        'attr': 'Total Acid Number',
        'unit': 'mg/g',
        'cls': MassFraction,
        'element_of': 'industry_properties',
    },
    norm('Sulfur, wt%'): {
        'attr': 'Sulfur Mass Fraction',
        'unit': '%',
        'cls': MassFraction,
        'element_of': 'bulk_composition',
    },
    #
    # Viscosity at 20C/68F, cSt (not a simple map)
    #
    # Viscosity at 40C/104F, cSt (not a simple map)
    #
    # Viscosity at 50C/122F, cSt (not a simple map)
    #
    norm('Mercaptan sulfur, ppm'): {
        'attr': 'Mercaptan Sulfur Mass Fraction',
        'unit': 'ppm',
        'cls': MassFraction,
        'num_digits': 4,
        'convert_from': 'ppm',
        'element_of': 'bulk_composition',
    },
    norm('Nitrogen, ppm'): {
        'attr': 'Nitrogen Mass Fraction',
        'unit': 'ppm',
        'cls': MassFraction,
        'element_of': 'bulk_composition',
    },
    norm('CCR, wt%'): {
        'attr': 'Conradson Carbon Residue',
        'unit': '%',
        'cls': MassFraction,
        'element_of': 'industry_properties',
    },
    norm('N-Heptane Insolubles (C7 Asphaltenes), wt%'): {
        'attr': 'SARA.asphaltenes',
        'unit': '%',
        'cls': MassFraction,
    },
    norm('Nickel, ppm'): {
        'attr': 'Nickel Mass Fraction',
        'unit': 'ppm',
        'cls': MassFraction,
        'element_of': 'bulk_composition',
    },
    norm('Vanadium, ppm'): {
        'attr': 'Vanadium Mass Fraction',
        'unit': 'ppm',
        'cls': MassFraction,
        'element_of': 'bulk_composition',
    },
    norm('Calcium, ppm'): {
        'attr': 'Calcium Mass Fraction',
        'unit': 'ppm',
        'cls': MassFraction,
        'convert_from': 'ppm',
        'element_of': 'bulk_composition',
    },
    norm('Reid Vapor Pressure (RVP) Whole Crude, psi'): {
        'attr': 'Reid Vapor Pressure',
        'unit': 'Pa',
        'cls': Pressure,
        'convert_from': 'psi',
        'element_of': 'industry_properties',
    },
    norm('Hydrogen Sulfide (dissolved), ppm'): {
        'attr': 'Hydrogen Sulfide Concentration',
        'unit': 'ppm',
        'cls': MassFraction,  # concentration??
        'element_of': 'bulk_composition',
    },
    norm('Salt content, ptb'): {
        'attr': 'Salt Content',
        'unit': 'ppm',
        'cls': MassFraction,
        'convert_from': 'ppb',  # conversion for pounds/thousand barrels??
        'element_of': 'bulk_composition',
    },
    norm('Paraffins, vol %'): {
        'attr': 'Paraffin Volume Fraction',
        'unit': '%',
        'cls': VolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Naphthenes, vol %'): {
        'attr': 'Naphthene Volume Fraction',
        'unit': '%',
        'cls': VolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Aromatics (FIA), vol %'): {
        'attr': 'SARA.aromatics',
        'unit': '%',
        'cls': VolumeFraction,
    },
    #
    # Bunch of distillation props (not a simple map)
    #
    norm('Freeze point, F'): {
        'attr': 'Freeze Point',
        'unit': 'C',
        'convert_from': 'F',
        'cls': Temperature,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Smoke point, mm'): {
        'attr': 'Smoke Point',
        'unit': 'mm',
        'cls': Length,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Naphthalenes (D1840), vol%'): {
        'attr': 'Naphthalene Volume Fraction',
        'unit': '%',
        'cls': VolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    #
    # Viscosity at 100C/212F, cSt (not a simple map)
    #
    # Viscosity at 150C/302F, cSt (not a simple map)
    #
    norm('Cetane Index 1990 (D4737),'): {
        'attr': 'Cetane Index 1990 (D4737)',
        'unit': 'dimensionless',
        'cls': UnittedValue,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Cloud point, F'): {
        'attr': 'Cloud Point',
        'unit': 'C',
        'convert_from': 'F',
        'cls': Temperature,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Aniline pt, F'): {
        'attr': 'Aniline Point',
        'unit': 'C',
        'convert_from': 'F',
        'cls': Temperature,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
}


def ExxonMapper(record):
    """
    Accepts and Exxon record:

    tuple of:
      - oil name
      - list of lists of the spreadsheet contents

    returns an Oil Object
    """
    name, data = record
    data = iter(data)

    reference = read_header(data)

    oil_id, ref_id, sample_names = read_identification(data)

    oil = Oil(oil_id=oil_id)
    oil.metadata.name = name
    oil.metadata.product_type = 'crude'
    oil.metadata.reference = reference
    oil.metadata.source_id = ref_id

    samples = SampleList([Sample(**sample_id_attrs(name))
                          for name in sample_names
                          if name is not None])

    cut_table = read_cut_table(sample_names, data)

    create_middle_tier_objs(samples)

    set_boiling_point_range(samples, cut_table)

    apply_map(data, cut_table, samples)

    process_cut_table(oil, samples, cut_table)

    return oil


def read_header(data):
    '''
        fixme: this should probably be more flexible
               but we can wait 'till we get data that doesn't match
        it could / should read the whole dist cut table, then map it
        to the samples Exxon info in the header
    '''
    ref_text = "\n".join([next(data)[0] for _ in range(3)])
    years = [int(n) for n in re.compile(r'\b\d{4}\b').findall(ref_text)]

    if len(years) == 0:
        ref_year = None  # need to get file props from the .xlsx file
    else:
        ref_year = max(years)

    return Reference(reference=ref_text, year=ref_year)


def read_identification(data):
    row = next_non_empty(data)

    return f'EX{next_id():06}', f'{row[0]}', row[1:]


def sample_id_attrs(name):
    if name == 'Whole crude':
        name = 'Fresh Oil Sample'
        short_name = 'Fresh Oil'
    else:
        short_name = f'{name[:12]}...'

    return {'metadata': SampleMetaData(name=name, short_name=short_name)}


def create_middle_tier_objs(samples):
    '''
        These are the dataclasses that comprise the attributes of the Sample
    '''
    for sample in samples:
        sample.physical_properties = PhysicalProperties()
        sample.environmental_behavior = EnvironmentalBehavior()
        sample.SARA = Sara()


def read_cut_table(sample_names, data):
    '''
        Read the rest of the rows and save them in a dictionary.
        - key: first field of the row
        - value: the rest of the fields as a list.  The index position in the
          list will be correlated to the sample names that were captured.

        Note: Some datasheets (curlew) have some empty columns in between
              the sample data and the properties column.  So we need to make
              sure there actually exists a sample name field before adding
              it to our cut table data.
    '''
    cut_table = {}

    while True:
        try:
            row = next_non_empty(data)

            sample_attr = norm(row[0])
            sample_data = [f for f, n in zip(row[1:], sample_names)
                           if n is not None]

            cut_table[sample_attr] = sample_data
        except StopIteration:
            break

    return cut_table


def set_boiling_point_range(samples, cut_table):
    '''
        Parse the names to determine the boiling point ranges
        Requires the sample names to be initialized

        Need to know:
        - Initial boiling point (IBF)
        - End boiling point (EP)
    '''
    initial_bp = sigfigs(cut_table['ibp, f'][0], 5)
    final_bp = sigfigs(cut_table['ep, f'][-1], 5)

    for sample_prev, sample in zip(samples, samples[1:]):
        prev_max_temp = to_number(sample_prev.metadata.name.split()[-1])
        min_temp, _sep, max_temp = [to_number(n)
                                    for n in sample.metadata.name.split()[-3:]]

        if min_temp == 'IBP':
            min_temp = initial_bp
        elif not isinstance(min_temp, float):
            min_temp = prev_max_temp

        sample.metadata.boiling_point_range = Temperature(min_value=min_temp,
                                                          max_value=max_temp,
                                                          unit='F')

    # fix the last sample
    last_bpr = samples[-1].metadata.boiling_point_range
    last_bpr.min_value = last_bpr.max_value
    last_bpr.max_value = final_bp


def apply_map(data, cut_table, samples):
    for name, data in MAPPING.items():
        row = cut_table[name]
        set_sample_property(samples, row, **data)


def set_sample_property(samples, row, attr, unit, cls,
                        convert_from=None, element_of=None,
                        num_digits=5):
    """
    reads a row from the spreadsheet, and sets the sample properties

    Notes:
    - optional rounding to "num_digits" digits
    - optional converting to unit from convert_from (if the the data aren't in
    the right units)
    - These values are now kept in a list of compounds held by the
      bulk_composition attribute
    - Ideally, the name & groups of each compound would have the
      original field text from the datasheet.
    """
    for sample, val in zip(samples, row):
        if val is not None and val not in ('NotAvailable',):
            if convert_from is not None:
                val = uc.convert(convert_from, unit, val)

            if element_of is None:
                # assign to an attribute
                if isinstance(attr, str):
                    attr = attr.split('.')

                if len(attr) > 1:
                    for a in attr[:-1]:
                        child_value = getattr(sample, a)

                        if child_value is None:
                            # get a default value from the parent dataclass
                            # annotation
                            child_value = sample.__dataclass_fields__[a].type()
                            setattr(sample, a, child_value)

                        sample = child_value

                setattr(sample, attr[-1],
                        cls(sigfigs(val, num_digits), unit=unit))
            else:
                # add to a list attribute
                compositions = getattr(sample, element_of)

                compositions.append(Compound(
                    name=attr,
                    measurement=cls(sigfigs(val, num_digits), unit=unit)
                ))


def process_cut_table(oil, samples, cut_table):
    """
    process the parts that aren't a simple map
    """
    # API -- odd because we only need one!
    row = cut_table[norm("API Gravity,")]

    # pull API from first value
    try:
        # stored as full precision double
        oil.metadata.API = round(float(row[0]), 1)
    except Exception:
        oil.metadata.API = None

    # use specific gravity to get density
    row = cut_table[norm("Specific Gravity (60/60F)")]
    for sample, val in zip(samples, row):
        try:
            rho = uc.convert("SG", "g/cm^3", val)
            sample.physical_properties.densities.append(DensityPoint(
                density=Density(value=sigfigs(rho, 5), unit="g/cm^3"),
                ref_temp=Temperature(value=15.6, unit="C"),
            ))

        except Exception:
            pass

    # viscosity
    for lbl in ("Viscosity at 20C/68F, cSt",
                "Viscosity at 40C/104F, cSt",
                "Viscosity at 50C/122F, cSt"):
        row = cut_table[norm(lbl)]

        temps = re.compile(r'\d+C').findall(lbl)
        if len(temps) > 0:
            temp_c = float(temps[0][:-1])
        else:
            temp_c = None

        for sample, val in zip(samples, row):
            try:
                sample.physical_properties.kinematic_viscosities.append(
                    KinematicViscosityPoint(
                        viscosity=KinematicViscosity(value=sigfigs(val, 5),
                                                     unit="cSt"),
                        ref_temp=Temperature(value=temp_c, unit="C"),
                    )
                )
            except Exception:
                pass

    # distillation data
    if norm("Distillation type, TBP") not in cut_table:
        raise ValueError("I don't recognise this distillation data. \n"
                         'Expected: "Distillation type, TBP"')

    for sample in samples:
        sample.distillation_data.type = 'volume fraction'

    for name, row in cut_table.items():
        if norm("vol%, F") in name or name == norm("IBP, F"):
            # looks like a distillation cut.
            percent = 0.0 if "ibp" in name else float(name.split("vol")[0])

            for sample, val in zip(samples, row):
                if val is not None:
                    val = sigfigs(uc.convert("F", "C", val), 5)

                    sample.distillation_data.cuts.append(DistCut(
                        fraction=MassFraction(value=percent, unit="%"),
                        vapor_temp=Temperature(value=val, unit="C")
                    ))
        elif name == norm('EP, F'):
            for sample, val in zip(samples, row):
                if val is not None:
                    val = sigfigs(uc.convert("F", "C", val), 5)

                    sample.distillation_data.end_point = Temperature(value=val,
                                                                     unit="C")

    # sort them
    for sample in samples:
        sample.distillation_data.cuts.sort(key=lambda c: c.fraction.value)

    oil.sub_samples = samples

    return oil


# Utilities:
def next_non_empty(data):
    while True:
        row = next(data)

        if not is_empty(row):
            break

    return row


def is_empty(row):
    return all([f is None for f in row])


def get_next_properties_row(data, exp_field):
    row = next_non_empty(data)

    if norm(row[0]) != norm(exp_field):
        raise ValueError(f'Something wrong with data sheet: {row}, '
                         'expected: {exp_field}')

    return row


def to_number(field):
    '''
        Try to extract a number from a text field.  Within this scope, we
        don't care to try extract any unit information, just the number.
        Some variations on numeric data fields in the Exxon Assays:
        - '1000F+'
        - '1000F'
        - '650'
        - 'C5' is not numeric
    '''
    try:
        return float(field)
    except Exception:
        pass

    try:
        return float(re.search('^[0-9\\.]+', field).group(0))
    except Exception:
        pass

    return field
