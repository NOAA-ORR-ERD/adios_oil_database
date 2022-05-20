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
    ######
    # This is mapping of the fields in the main cut data table section.
    # It tells us what to do with the values and where to put them
    # relative to a sample.
    ######
    #
    # Yield (% wt) - no place to map this.
    #
    norm('Yield (% vol)'): {
        'attr': 'cut_volume',
        'unit': '%',
        'cls': VolumeFraction,
        'num_digits': 6,
    },
    #
    # Cumulative Yield (% wt) - Alternate representation of Yield (% wt).
    #                           Nearly the same data.
    #
    # Volume Average B.P. (\N{DEGREE SIGN}F) - industry properties maybe???
    #
    # Density @ 59\N{DEGREE SIGN}F (g/cc) - same as API
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
    # Viscosity @ 68 F (cSt) - (not a simple map)
    #
    # Viscosity @ 104 F (cSt) - (not a simple map)
    #
    # Viscosity @ 122 F (cSt) - (not a simple map)
    #
    # Viscosity @ 140 F (cSt) - (not a simple map)
    #
    # Viscosity @ 212 F (cSt) - (not a simple map)
    #
    # Viscosity @ 266 F (cSt) - (not a simple map)
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
    norm('Wax (% wt)'): {
        'attr': 'Wax Mass Fraction',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    norm('C7 Asphaltenes (% wt)'): {
        'attr': 'C7 Asphaltene Mass Fraction',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'bulk_composition',
    },
    #
    # Micro Carbon Residue (% wt) - is this the same as CCR???
    #
    norm('Micro Carbon Residue (% wt)'): {
        'attr': 'Micro Carbon Residue',
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
}


WHOLE_CRUDE_MAPPING = {
    ######
    # This is mapping of the fields in the 'Whole Crude Properties' table
    # section.  It tells us what to do with the values and where to put them
    # relative to a sample.
    #
    # The section 'Whole Crude Properties' contains properties that are
    # mostly redundant, and can be found in the 'IBP - FBP' cut data.
    # So I think we can be fairly sure that this cut is the 'Fresh Oil'
    # sub-sample.
    # All props below here are unique to the Whole Crude Properties section.
    # I think we can map these properties to the 'IBP - FBP' sub-sample.
    ######
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


MOLECULES_MAPPING = {
    ######
    # This is mapping of the fields in the 'Molecules' table section.
    # It tells us what to do with the values and where to put them
    # relative to a sample.
    ######
    norm('methane + ethane'): {
        'attr': 'Methane + Ethane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('propane'): {
        'attr': 'Propane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('isobutane'): {
        'attr': 'Isobutane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('n-butane'): {
        'attr': 'N-Butane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('isopentane'): {
        'attr': 'Isopentane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('n-pentane'): {
        'attr': 'N-Pentane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('cyclopentane'): {
        'attr': 'Cyclopentane',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('c6 paraffins'): {
        'attr': 'C6 Paraffins',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('c6 naphthenes'): {
        'attr': 'C6 Naphthenes',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('benzene'): {
        'attr': 'Benzene',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['BTEX Group'],
    },
    norm('c7 paraffins'): {
        'attr': 'C7 Paraffins',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('c7 naphthenes'): {
        'attr': 'C7 Naphthenes',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['Molecules'],
    },
    norm('toluene'): {
        'attr': 'Toluene',
        'unit': '%',
        'unit_type': 'massfraction',
        'cls': MassOrVolumeFraction,
        'element_of': 'compounds',
        'groups': ['BTEX Group'],
    },
}

# concatenate our mappings
SUBSAMPLE_MAPPING.update(WHOLE_CRUDE_MAPPING)
SUBSAMPLE_MAPPING.update(MOLECULES_MAPPING)

# include any misspellings here
SUBSAMPLE_MAPPING[norm('Naphthenes (%wt)')] = SUBSAMPLE_MAPPING[
    norm('Naphthenes (% wt)')
]
SUBSAMPLE_MAPPING[norm('Reid Vapor Pressure (psi)')] = SUBSAMPLE_MAPPING[
    norm('Reid Vapour Pressure (psi)')
]


def ExxonMapperV2(record):
    """
    Accepts and Exxon record:

    tuple of:
      - oil name
      - list of lists of the spreadsheet contents

    returns an Oil Object
    """
    try:
        name, [data, graph_data, *_] = record
    except ValueError:
        # not all of the new records have graph data
        name, [data, *_] = record
        graph_data = None

    reference = get_reference(iter(data))
    general_info = read_general_info(data)
    molecules = read_molecules(data)
    whole_crude_properties = read_whole_crude_properties(data)

    oil = Oil(oil_id=f'EX{next_id():05}')

    load_metadata(oil, name, reference, general_info, whole_crude_properties)

    sample_names, samples = generate_samples(data)

    load_distillation_data(samples, graph_data)

    cut_table = read_cut_table(sample_names, data)

    set_boiling_point_range(samples, cut_table)

    set_all_sample_properties(samples, cut_table, molecules,
                              whole_crude_properties)

    # now we perform all the not-so-simple mapping

    load_densities(samples, cut_table)

    load_viscosities(samples, cut_table)

    normalize_samples(samples)

    oil.sub_samples = samples

    return oil


def get_reference(data):
    """
    Get the reference information
    """
    ref_text = [next(data)[0] for _ in range(2)]
    ref_text = "\n".join([i for i in ref_text if i is not None])
    years = [int(n) for n in re.compile(r'\b\d{4}\b').findall(ref_text)]

    if len(years) == 0:
        ref_year = None  # need to get file props from the .xlsx file
    else:
        ref_year = max(years)

    ref = Reference(reference=ref_text, year=ref_year)
    ref.reference += (
        '\nSource: https://corporate.exxonmobil.com/'
        'Crude-oils/Crude-trading/Assays-available-for-download'
        '\nAccessed: Dec 9th, 2020')
    ref.year = 2020

    return ref


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


def load_metadata(oil, name, reference, general_info, whole_crude_properties):
    """
    Here we will load all the oil metadata from the source data
    """
    oil.metadata.name = name
    oil.metadata.source_id = general_info['reference']
    oil.metadata.location = general_info['origin']
    oil.metadata.reference = reference
    oil.metadata.product_type = 'Crude Oil NOS'

    try:
        oil.metadata.sample_date = general_info['sample date'].isoformat()
    except AttributeError:
        oil.metadata.sample_date = general_info['assay date'].isoformat()

    try:
        # stored as full precision double
        oil.metadata.API = round(float(whole_crude_properties['API Gravity']),
                                 1)
    except Exception:
        oil.metadata.API = None

    oil.metadata.comments = general_info['comments']


def generate_samples(data):
    """
    Generate a list of sample names with column indexes, and an associated
    list of not-yet-populated sample objects.
    """
    sample_names = {}
    section = slice_record(data, [1, 34], [15, 2])
    sample_ranges = [i for i in itertools.zip_longest(*section,
                                                      fillvalue=None)]

    sample_names.update(dict(
        get_cut_item(sample_ranges, 1, 2, '')
    ))

    sample_names.update(dict(
        get_cut_item(sample_ranges, 2, 11, '(Atmospheric Cut)')
    ))

    sample_names.update(dict(
        get_cut_item(sample_ranges, 11, 15, '(Vacuum Cut)')
    ))

    samples = SampleList([Sample(**sample_id_attrs(name))
                          for name in sample_names
                          if name is not None])

    create_middle_tier_objs(samples)

    return sample_names, samples


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

        cut_name = f'{start} - {end}'

        if cut_name == 'IBP - FBP':
            cut_name = 'Fresh Oil Sample'
        elif label:
            cut_name = f'{cut_name} {label}'

        yield (cut_name, i)


def sample_id_attrs(name):

    if name == 'Fresh Oil Sample':
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
                                    for n in sample.metadata.name.split()[:3]]

        if (min_temp, max_temp) == ('Fresh', 'Sample'):
            continue

        if min_temp in ('IBP', 'C5'):
            # From Dalina: C5 is pentane, but there are different isomers
            #              of pentane, and they have different Boiling Points.
            #              The one with the lowest BP isomer that we found is
            #              2,2-dimethylpropane -- 9.5 C (49F) so let's use that
            #              as the initial boiling point for the distillation.
            min_temp = 49.0

        if max_temp == 'FBP':
            if len(samples[0].distillation_data.cuts) > 0:
                # use the last temperature in the cuts
                max_temp = (samples[0].distillation_data.cuts[-1]
                            .vapor_temp.value)
            else:
                max_temp = None

        sample.metadata.boiling_point_range = Temperature(min_value=min_temp,
                                                          max_value=max_temp,
                                                          unit='F')


def set_all_sample_properties(samples, cut_table, molecules,
                              whole_crude_properties):
    for name, data in cut_table.items():
        sample = find_sample(samples, name)

        if sample is not None:
            set_sample_properties(sample, data)

    set_sample_properties(samples[0], molecules)
    set_sample_properties(samples[0], whole_crude_properties)


def find_sample(samples, name):
    ret = [s for s in samples if s.metadata.name == name]
    return ret[0] if len(ret) > 0 else None


def set_sample_properties(sample, sample_properties):
    for name, value in sample_properties.items():
        set_sample_property(sample, name, value)


def set_sample_property(sample, name, value):
    """
    Set a single property of a sample object.  The mapping table will control
    how the property get set.
    """
    if name is not None and norm(name) in SUBSAMPLE_MAPPING:
        # print(f'We got a mapping for "{name}"')
        mapping = SUBSAMPLE_MAPPING[norm(name)]
        apply_mapping(sample, value, **mapping)
    # else:
    #     print(f'No mapping for "{name}"')


def apply_mapping(sample, value,
                  attr,
                  unit,
                  cls,
                  unit_type=None,
                  convert_from=None,
                  element_of=None,
                  num_digits=5,
                  groups=None):
    if value is not None and value not in ('NotAvailable', '-'):
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
            item_cls = compositions.item_type

            if attr in [c.name for c in compositions]:
                # list item is already there, don't duplicate it.
                return

            measurement = cls(sigfigs(value, num_digits), unit=unit,
                              unit_type=unit_type)

            kwargs = {
                'name': attr,
                'measurement': measurement,
            }

            if ('groups' in item_cls.__dataclass_fields__ and
                    groups is not None):
                kwargs['groups'] = groups

            compositions.append(item_cls(**kwargs))


def load_densities(samples, cut_table):
    """
    There is only one density per sample, but it is not a simple mapping.
    """
    for sample in samples:
        cut = cut_table[sample.metadata.name]

        for lbl in ('Density @ 59\N{DEGREE SIGN}F (g/cc)',):
            ref_temp, ref_temp_unit = lbl.split()[2].split('\N{DEGREE SIGN}')
            rho = cut[lbl]

            if rho is not None:
                ref_temp = uc.convert(ref_temp_unit, 'C', sigfigs(ref_temp, 5))

                sample.physical_properties.densities.append(DensityPoint(
                    density=Density(value=sigfigs(rho, 5), unit="g/cm^3"),
                    ref_temp=Temperature(value=sigfigs(ref_temp, 5), unit='C'),
                ))


def load_viscosities(samples, cut_table):
    for sample in samples:
        cut = cut_table[sample.metadata.name]

        for lbl in ('Viscosity @ 68 F (cSt)',
                    'Viscosity @ 104 F (cSt)',
                    'Viscosity @ 122 F (cSt)',
                    'Viscosity @ 140 F (cSt)',
                    'Viscosity @ 212 F (cSt)',
                    'Viscosity @ 266 F (cSt)'):
            ref_temp, ref_temp_unit = lbl.split()[2:4]
            mu_unit = lbl.split()[-1].strip('()')
            mu = cut[lbl]

            if mu is not None:
                ref_temp = uc.convert(ref_temp_unit, 'C', sigfigs(ref_temp, 5))

                sample.physical_properties.kinematic_viscosities.append(
                    KinematicViscosityPoint(
                        viscosity=KinematicViscosity(value=sigfigs(mu, 5),
                                                     unit=mu_unit),
                        ref_temp=Temperature(value=ref_temp, unit='C'),
                    ))


def load_distillation_data(samples, graph_data):
    """
    We will load the distillation graph data on the first sample only
    """
    if graph_data is None:
        return

    section = slice_record(graph_data, [1, 59], [3, 100])
    col_keys = section[0]

    data_points = [dict([(k, sigfigs(v, 5)) for k, v in zip(col_keys, r)])
                   for r in section[1:]
                   if not all([d is None for d in r])]

    s = samples[0]

    s.distillation_data.type = 'mass fraction'
    s.distillation_data.fraction_recovered = MassFraction(
        value=1.0,
        unit='fraction'
    )

    # generate the cuts (Wgt % only)
    for dp in data_points:
        # ref_temp = uc.convert('F', 'C', dp['Boiling Point'])
        ref_temp = dp['Boiling Point']
        fraction = dp['Wgt']

        s.distillation_data.cuts.append(DistCut(
            fraction=MassFraction(value=fraction, unit="%"),
            vapor_temp=Temperature(value=ref_temp, unit="F")
        ))

    end_point = data_points[-1]['Boiling Point']
    s.distillation_data.end_point = Temperature(value=end_point, unit="F")


def normalize_samples(samples):
    """
    Not sure what to call this function.  Basically, we will fix any data
    issues that couldn't be handled in the mapping stages.
    """
    if samples[0].metadata.name == 'Fresh Oil Sample':
        # set the cut volume to 100%
        samples[0].cut_volume = VolumeFraction(100.0, unit="%")
