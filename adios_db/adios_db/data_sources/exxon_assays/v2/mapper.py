#!/usr/bin/env python
"""
Exxon Mapper Version 1

Not really a class -- it's really a function that build up an
oil object
"""
import re
import logging
import itertools

import nucos as uc

from adios_db.util import sigfigs
from adios_db.models.common.measurement import (
    Temperature,
    MassFraction,
    VolumeFraction,
    MassOrVolumeFraction,
    Density,
    KinematicViscosity,
    Pressure,
    Unitless,
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
from adios_db.models.oil.compound import Compound
from adios_db.models.oil.physical_properties import PhysicalProperties
from adios_db.models.oil.environmental_behavior import EnvironmentalBehavior
from adios_db.models.oil.sara import Sara

from ..common import next_id, norm, to_number

import pdb
from pprint import pprint

logger = logging.getLogger(__name__)


SUBSAMPLE_MAPPING = {
    norm('Yield (% vol)'): {
        'attr': 'cut_volume',
        'unit': '%',
        'cls': VolumeFraction,
        'num_digits': 6,
    },
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
    # Cumulative Yield (% wt)
    #
    # Volume Average B.P. (\N{DEGREE SIGN}F) - industry properties maybe???
    #
    # Densiy @ 59\N{DEGREE SIGN}F (g/cc) - same as API
    #
    # API gravity,  # not a simple map
    #
    # UOPK - The K factor or characterization factor is a systematic way of
    #        classifying a crude oil according to its paraffinic, naphthenic,
    #        intermediate or aromatic nature. 12.5 or higher indicate a
    #        crude oil of predominantly paraffinic constituents, while 10 or
    #        lower indicate a crude of more aromatic nature.
    #        The K factor is also referred to as the UOP K factor or just UOPK.
    #        So where do we put it?  Industry properties??
    #
    # Molecular Weight (g/mol) - looks like we had this in the model once,
    #                            but not anymore. Physical properties maybe??
    #
    norm('Total Sulphur (% wt)'): {
        'attr': 'Sulfur Mass Fraction',
        'unit': '%',
        'unit_type': 'mass fraction',
        'cls': MassOrVolumeFraction,
        'num_digits': 5,
        'element_of': 'bulk_composition',
    },
    norm('Mercaptan Sulphur (ppm)'): {
        'attr': 'Mercaptan Sulfur Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'num_digits': 4,
        'element_of': 'bulk_composition',
    },
    norm('Total Nitrogen (ppm)'): {
        'attr': 'Nitrogen Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Total Acid Number (mgKOH/g)'): {
        'attr': 'Total Acid Number',
        'unit': 'mg/g',
        'unit_type': 'MassFraction',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
    },
    #
    # Viscosity at 20C/68F, cSt (not a simple map)
    #
    # Viscosity at 40C/104F, cSt (not a simple map)
    #
    # Viscosity at 50C/122F, cSt (not a simple map)
    #
    # Viscosity at 100C/212F, cSt (not a simple map)
    #
    # Viscosity at 150C/302F, cSt (not a simple map)
    #
    # RON (Clear) - ???
    #
    # MON (Clear) - ???
    #
    norm('Paraffins (% wt)'): {
        'attr': 'Paraffin Mass Fraction',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Naphthenes (% wt)'): {
        'attr': 'Naphthene Mass Fraction',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Aromatics (% wt)'): {
        'attr': 'Aromatics',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Pour Point (\N{DEGREE SIGN}F)'): {
        'attr': 'physical_properties.pour_point.measurement',
        'unit': 'C',
        'cls': Temperature,
        'num_digits': 8,
        'convert_from': 'F',
    },
    norm('Cloud Point (\N{DEGREE SIGN}F)'): {
        'attr': 'Cloud Point',
        'unit': 'F',
        'unit_type': 'temperature',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Freeze Point (\N{DEGREE SIGN}F)'): {
        'attr': 'Freeze Point',
        'unit': 'F',
        'unit_type': 'temperature',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Smoke Point (mm)'): {
        'attr': 'Smoke Point',
        'unit': 'mm',
        'unit_type': 'length',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Cetane Index'): {
        'attr': 'Cetane Index',
        'unit': None,
        'unit_type': 'unitless',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Naphthalenes (% vol)'): {
        'attr': 'Naphthalene Volume Fraction',
        'unit': '%',
        'cls': VolumeFraction,
        'convert_from': '%',
        'element_of': 'bulk_composition',
    },
    norm('Aniline Point (\N{DEGREE SIGN}F)'): {
        'attr': 'Aniline Point',
        'unit': 'F',
        'unit_type': 'Temperature',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
        'num_digits': 6,
    },
    norm('Hydrogen (% wt)'): {
        'attr': 'Hydrogen Mass Fraction',
        'unit': '%',
        'unit_type': 'mass fraction',
        'cls': MassOrVolumeFraction,
        'num_digits': 4,
        'element_of': 'bulk_composition',
    },
    #
    # Wax (% wt) - ???
    #
    norm('C7 Asphaltenes (% wt)'): {
        'attr': 'C7 Asphaltenes)',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    #
    # Micro Carbon Residue (% wt) - is this the same as CCR???
    #
    norm('CCR, wt%'): {
        'attr': 'Conradson Carbon Residue',
        'unit': '%',
        'unit_type': 'MassFraction',
        'cls': AnyUnit,
        'element_of': 'industry_properties',
    },
    norm('Vanadium (ppm)'): {
        'attr': 'Vanadium Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Nickel (ppm)'): {
        'attr': 'Nickel Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Iron (ppm)'): {
        'attr': 'Iron Mass Fraction',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    #
    #  All props below here are found in the Whole Crude Properties only.
    #
    norm('Salt content, ptb'): {
        'attr': 'Salt Content',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'convert_from': 'ppb',  # conversion for pounds/thousand barrels??
        'element_of': 'bulk_composition',
    },
    norm('Hydrogen Sulphide (ppm)'): {
        'attr': 'Hydrogen Sulfide Concentration',
        'unit': 'ppm',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('Reid Vapour Pressure (psi)'): {
        'attr': 'Reid Vapor Pressure',
        'unit': 'psi',
        'cls': AnyUnit,
        'unit_type': 'pressure',
        'convert_from': 'psi',
        'element_of': 'industry_properties',
    },
}

# include any misspellings here
SUBSAMPLE_MAPPING[norm('Naphthenes (%wt)')] = SUBSAMPLE_MAPPING[
    norm('Naphthenes (% wt)')
]


def ExxonMapperV2(record):
    """
    Accepts and Exxon record:

    tuple of:
      - oil name
      - list of lists of the spreadsheet contents

    returns an Oil Object
    """
    name, data = record
    data, graph_data, *_ = data

    reference = read_header(iter(data))
    reference.reference += (
        '\nSource: https://corporate.exxonmobil.com/Crude-oils/Crude-trading/Assays-available-for-download'
        '\nAccessed: Dec 9th, 2020')
    reference.year = 2020

    general_info = read_general_info(data)
    molecules = read_molecules(data)
    whole_crude_properties = read_whole_crude_properties(data)

    oil_id = f'EX{next_id():05}'
    ref_id = general_info['reference']
    sample_names = read_sample_names(data)

    oil = Oil(oil_id=oil_id)
    oil.metadata.name = name
    oil.metadata.product_type = 'Crude Oil NOS'
    oil.metadata.reference = reference
    oil.metadata.source_id = ref_id

    samples = SampleList([Sample(**sample_id_attrs(name))
                          for name in sample_names
                          if name is not None])

    create_middle_tier_objs(samples)

    cut_table = read_cut_table(sample_names, data)

    set_boiling_point_range(samples, cut_table)

    set_all_sample_properties(cut_table, samples)

    #apply_map(cut_table, samples)

    process_cut_table(oil, samples, cut_table)

    return oil


def read_header(data):
    """
    fixme: this should probably be more flexible
    but we can wait 'till we get data that doesn't match
    it could / should read the whole dist cut table, then map it
    to the samples Exxon info in the header
    """
    ref_text = [next(data)[0] for _ in range(2)]
    ref_text = "\n".join([i for i in ref_text if i is not None])
    years = [int(n) for n in re.compile(r'\b\d{4}\b').findall(ref_text)]

    if len(years) == 0:
        ref_year = None  # need to get file props from the .xlsx file
    else:
        ref_year = max(years)

    return Reference(reference=ref_text, year=ref_year)


def read_general_info(data):
    section = slice_record(data, [1, 13], [5, 15])

    return dict([
        (norm(k), v) for k, v, *_ in section if k is not None
    ])


def read_molecules(data):
    section = slice_record(data, [6, 13], [5, 15])

    return dict([
        (k.strip(), v)
        for k, *_, v in section
        if k is not None
    ])


def read_whole_crude_properties(data):
    section = slice_record(data, [11, 13], [5, 15])

    return dict([
        (k.strip(), v)
        for k, *_, v in section
        if k is not None
    ])


def slice_record(record, position, size):
    """
    Slice a 2d portion of our record, which is a 2d list of lists.
    """
    [x, y], [w, h] = position, size

    return [[c for i, c in enumerate(r) if x <= i < x + w]
            for i, r in enumerate(record)
            if y <= i < y + h]


def flatten_2d(list_in):
    return [i for sub in list_in for i in sub]


def read_sample_names(data):
    samples = {}
    section = slice_record(data, [1, 34], [15, 2])
    sample_ranges = [i for i in itertools.zip_longest(*section,
                                                      fillvalue=None)]

    samples.update(dict(
        get_cut_item(sample_ranges, 1, 2, '')
    ))

    samples.update(dict(
        get_cut_item(sample_ranges, 2, 11, 'Atmospheric Cuts:')
    ))

    samples.update(dict(
        get_cut_item(sample_ranges, 11, 15, 'Vacuum Cuts:')
    ))

    return samples


def get_cut_item(sample_ranges, first, last, label):
    for i in range(first, last):
        start, end = sample_ranges[i]

        try:
            start = start.strip()
        except AttributeError:
            pass

        try:
            end = end.strip()
        except AttributeError:
            pass

        if label:
            yield (f'{label} {start} - {end}', i)
        else:
            yield (f'{start} - {end}', i)


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

    - key: sample name

    - value: the rest of the fields as a dict.
    """
    cut_table = {}
    section = slice_record(data, [1, 38], [15, 49])
    keys = flatten_2d(slice_record(section, [0, 0], [1, 49]))

    for k, i in sample_names.items():
        values = flatten_2d(slice_record(section, [i, 0], [1, 49]))

        cut_table[k] = dict(zip(keys, values))

    return cut_table


def set_boiling_point_range(samples, cut_table):
    """
    Parse the names to determine the boiling point ranges
    Requires the sample names to be initialized

    Need to know:
    - Initial boiling point (IBF)
    - End boiling point (FBP)

    Note: The new format assay doesn't appear to have definite number fields
          for IBP and FBP.
    """
    for sample in samples:
        min_temp, _sep, max_temp = [to_number(n)
                                    for n in sample.metadata.name.split()[-3:]]

        min_temp = None if min_temp in ('IBP', 'C5') else min_temp
        max_temp = None if max_temp == 'FBP' else max_temp

        sample.metadata.boiling_point_range = Temperature(min_value=min_temp,
                                                          max_value=max_temp,
                                                          unit='F')


def set_all_sample_properties(cut_table, samples):
    for name, data in cut_table.items():
        sample = find_sample(samples, name)

        if sample is not None:
            set_sample_properties(sample, data)


def find_sample(samples, name):
    ret = [s for s in samples if s.metadata.name == name]
    return ret[0] if len(ret) > 0 else None


def set_sample_properties(sample, sample_properties):
    for name, value in sample_properties.items():
        set_sample_property(sample, name, value)

    print()


def set_sample_property(sample, name, value):
    """
    Set a single property of a sample object.  The mapping table will control
    how the property get set.
    """
    if name is not None and norm(name) in SUBSAMPLE_MAPPING:
        print(f'We got a mapping for "{name}"')
        mapping = SUBSAMPLE_MAPPING[norm(name)]
        apply_mapping(sample, value, **mapping)
    else:
        print(f'No mapping for "{name}"')


def apply_mapping(sample, value,
                  attr,
                  unit,
                  cls,
                  unit_type=None,
                  convert_from=None,
                  element_of=None,
                  num_digits=5):
    if value is not None and value not in ('NotAvailable', ):
        if convert_from is not None:
            value = uc.convert(convert_from, unit, value)

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

            setattr(sample, attr[-1], cls(sigfigs(value, num_digits),
                                          unit=unit))
        else:
            # add to a list attribute
            compositions = getattr(sample, element_of)

            measurement = cls(sigfigs(value, num_digits), unit=unit,
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
