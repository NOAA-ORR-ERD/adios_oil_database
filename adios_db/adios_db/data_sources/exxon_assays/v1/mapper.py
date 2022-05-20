#!/usr/bin/env python
"""
Exxon Mapper Version 1

Not really a class -- it's really a function that build up an
oil object
"""
import re
import logging

import nucos as uc

from adios_db.util import sigfigs
from adios_db.models.common.measurement import (
    Temperature,
    VolumeFraction,
    MassOrVolumeFraction,
    Density,
    KinematicViscosity,
    AnyUnit,
)

from adios_db.models.oil.physical_properties import (
    DensityPoint,
    KinematicViscosityPoint,
)

from adios_db.models.oil.distillation import DistCut
from adios_db.models.oil.values import Reference

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample, SampleList

from adios_db.models.oil.metadata import SampleMetaData
from adios_db.models.oil.physical_properties import PhysicalProperties
from adios_db.models.oil.environmental_behavior import EnvironmentalBehavior
from adios_db.models.oil.sara import Sara

from ..common import next_id, norm, next_non_empty, to_number

logger = logging.getLogger(__name__)


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
        'unit_type': 'mass fraction',
        'cls': MassOrVolumeFraction,
        'num_digits': 4,
        'element_of': 'bulk_composition',
    },
    norm('Hydrogen, wt %'): {
        'attr': 'Hydrogen Mass Fraction',
        'unit': '%',
        'unit_type': 'mass fraction',
        'cls': MassOrVolumeFraction,
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
        'unit_type': 'MassFraction',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
    },
    norm('Sulfur, wt%'): {
        'attr': 'Sulfur Mass Fraction',
        'unit': '%',
        'unit_type': 'mass fraction',
        'cls': MassOrVolumeFraction,
        'num_digits': 5,
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
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'num_digits': 4,
        'element_of': 'bulk_composition',
    },
    norm('Nitrogen, ppm'): {
        'attr': 'Nitrogen Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('CCR, wt%'): {
        'attr': 'Conradson Carbon Residue',
        'unit': '%',
        'unit_type': 'MassFraction',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
    },
    norm('N-Heptane Insolubles (C7 Asphaltenes), wt%'): {
        'attr': 'N-Heptane Insolubles (C7 Asphaltenes)',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Nickel, ppm'): {
        'attr': 'Nickel Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Vanadium, ppm'): {
        'attr': 'Vanadium Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Calcium, ppm'): {
        'attr': 'Calcium Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'convert_from': 'ppm',
        'element_of': 'bulk_composition',
    },
    norm('Reid Vapor Pressure (RVP) Whole Crude, psi'): {
        'attr': 'Reid Vapor Pressure',
        'unit': 'psi',
        'cls': AnyUnit,
        'unit_type': 'pressure',
        'convert_from': 'psi',
        'element_of': 'industry_properties',
    },
    norm('Hydrogen Sulfide (dissolved), ppm'): {
        'attr': 'Hydrogen Sulfide Concentration',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Salt content, ptb'): {
        'attr': 'Salt Content',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'convert_from': 'ppb',  # conversion for pounds/thousand barrels??
        'element_of': 'bulk_composition',
    },
    norm('Paraffins, vol %'): {
        'attr': 'Paraffin Volume Fraction',
        'unit': '%',
        'unit_type': 'volumefraction',
        'cls': MassOrVolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Naphthenes, vol %'): {
        'attr': 'Naphthene Volume Fraction',
        'unit': '%',
        'unit_type': 'volumefraction',
        'cls': MassOrVolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Aromatics (FIA), vol %'): {
        'attr': 'Aromatics (FIA)',
        'unit': '%',
        'unit_type': 'volumefraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    #
    # Bunch of distillation props (not a simple map)
    #
    norm('Freeze point, F'): {
        'attr': 'Freeze Point',
        'unit': 'F',
        'unit_type': 'temperature',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Smoke point, mm'): {
        'attr': 'Smoke Point',
        'unit': 'mm',
        'unit_type': 'length',
        'cls': AnyUnit,
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
        'unit': None,
        'unit_type': 'unitless',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Cloud point, F'): {
        'attr': 'Cloud Point',
        'unit': 'F',
        'unit_type': 'temperature',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Aniline pt, F'): {
        'attr': 'Aniline Point',
        'unit': 'F',
        'unit_type': 'Temperature',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
}


def ExxonMapperV1(record):
    """
    Accepts and Exxon record:

    tuple of:
      - oil name
      - list of lists of the spreadsheet contents

    returns an Oil Object
    """
    name, [data, *_] = record
    data = iter(data)

    reference = read_header(data)
    reference.reference += (
        '\nSource: https://corporate.exxonmobil.com/'
        'Crude-oils/Crude-trading/Assays-available-for-download'
        '\nAccessed: Dec 9th, 2020')
    reference.year = 2020

    oil_id, ref_id, sample_names = read_identification(data)

    oil = Oil(oil_id=oil_id)
    oil.metadata.name = name
    oil.metadata.product_type = 'Crude Oil NOS'
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
    """
    fixme: this should probably be more flexible
    but we can wait 'till we get data that doesn't match
    it could / should read the whole dist cut table, then map it
    to the samples Exxon info in the header
    """
    ref_text = [next(data)[0] for _ in range(3)]
    ref_text = "\n".join([i for i in ref_text if i is not None])
    years = [int(n) for n in re.compile(r'\b\d{4}\b').findall(ref_text)]

    if len(years) == 0:
        ref_year = None  # need to get file props from the .xlsx file
    else:
        ref_year = max(years)

    return Reference(reference=ref_text, year=ref_year)


def read_identification(data):
    row = next_non_empty(data)

    return f'EX{next_id():05}', f'{row[0]}', row[1:]


def sample_id_attrs(name):
    if name == 'Whole crude':
        name = 'Fresh Oil Sample'
        short_name = 'Fresh Oil'
    else:
        short_name = f'{name[:12]}...'

    return {'metadata': SampleMetaData(name=name, short_name=short_name)}


def create_middle_tier_objs(samples):
    """
    These are the dataclasses that comprise the attributes of the Sample
    """
    for sample in samples:
        sample.physical_properties = PhysicalProperties()
        sample.environmental_behavior = EnvironmentalBehavior()
        sample.SARA = Sara()


def read_cut_table(sample_names, data):
    """
    Read the rest of the rows and save them in a dictionary.

    - key: first field of the row

    - value: the rest of the fields as a list.  The index position in the
             list will be correlated to the sample names that were captured.

    :note: Some datasheets (curlew) have some empty columns in between
           the sample data and the properties column.  So we need to make
           sure there actually exists a sample name field before adding
           it to our cut table data.
    """
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
    """
    Parse the names to determine the boiling point ranges
    Requires the sample names to be initialized

    Need to know:
    - Initial boiling point (IBF)
    - End boiling point (EP)
    """
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


def set_sample_property(samples,
                        row,
                        attr,
                        unit,
                        cls,
                        unit_type=None,
                        convert_from=None,
                        element_of=None,
                        num_digits=5):
    """
    reads a row from the spreadsheet, and sets the sample properties

    Notes:

    - optional rounding to "num_digits" digits

    - optional converting to unit from convert_from
      (if the data aren't in the right units)

    - These values are now kept in a list of compounds held by the
      bulk_composition attribute

    - The name & groups of each compound should be match the
      ADIOS data model controlled vocabulary
    """
    for sample, val in zip(samples, row):
        if val is not None and val not in ('NotAvailable', ):
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

                setattr(sample, attr[-1], cls(sigfigs(val, num_digits),
                                              unit=unit))
            else:
                # add to a list attribute
                compositions = getattr(sample, element_of)

                measurement = cls(sigfigs(val, num_digits), unit=unit,
                                  unit_type=unit_type)
                item_cls = compositions.item_type
                compositions.append(item_cls(
                    name=attr,
                    measurement=measurement,
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
            sample.physical_properties.densities.append(
                DensityPoint(
                    density=Density(value=sigfigs(rho, 5), unit="g/cm^3"),
                    ref_temp=Temperature(value=15.6, unit="C"),
                ))

        except Exception:
            pass

    # viscosity
    for lbl in ("Viscosity at 20C/68F, cSt", "Viscosity at 40C/104F, cSt",
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
                    ))
            except Exception:
                pass

    # distillation data
    if norm("Distillation type, TBP") not in cut_table:
        raise ValueError("I don't recognise this distillation data. \n"
                         'Expected: "Distillation type, TBP"')

    for s in samples:
        s.distillation_data.type = 'volume fraction'
        s.distillation_data.fraction_recovered = VolumeFraction(
            value=1.0,
            unit='fraction'
        )

    for name, row in cut_table.items():
        if norm("vol%, F") in name or name == norm("IBP, F"):
            # looks like a distillation cut.
            percent = 0.0 if "ibp" in name else float(name.split("vol")[0])

            for sample, val in zip(samples, row):
                if val is not None:
                    val = sigfigs(uc.convert("F", "C", val), 5)

                    sample.distillation_data.cuts.append(DistCut(
                        fraction=VolumeFraction(value=percent, unit="%"),
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
