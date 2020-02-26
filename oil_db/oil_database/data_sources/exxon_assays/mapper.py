#!/usr/bin/env python
"""
Exxon Mapper

Not really a class -- it's really a function that build up an
oil object
"""
import logging

import unit_conversion as uc

from oil_database.util import sigfigs
from oil_database.models.oil.oil import Oil
from oil_database.models.oil.sample import Sample
from oil_database.models.oil.values import (UnittedValue,
                                            Density,
                                            Viscosity,
                                            DistCut,
                                            )

from pprint import PrettyPrinter
pprint = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


def norm(string):
    """
    normalizes a string for comparing

    so far: lower case, whitespace strip
    trailing and leading comma strip
    """
    return string.strip().strip(',').lower()


MAPPING = {
    norm("Mercaptan sulfur, ppm"): {
        "attr": "mercaptan_sulfur_mass_fraction",
        "unit": "ppm",
        "num_digits": 4,
        "convert_from": "ppm",
    },
    norm("Carbon, wt %"): {
        "attr": "carbon_mass_fraction",
        "unit": "%",
        "num_digits": 4,
    },
    norm("Hydrogen, wt %"): {
        "attr": "hydrogen_mass_fraction",
        "unit": "%",
        "num_digits": 4,
    },
    norm("Pour point, F"): {
        "attr": "pour_point",
        "unit": "C",
        "convert_from": "F",
    },
    norm("Nitrogen, ppm"): {
        "attr": "nitrogen_mass_fraction",
        "unit": "ppm",
    },
    norm("Neutralization number (TAN), MG/GM"): {
        "attr": "total_acid_number",
        "unit": "mg/kg",
    },
    norm("Sulfur, wt%"): {
        "attr": "sulfur_mass_fraction",
        "unit": "%",
    },
    norm("Reid Vapor Pressure (RVP) Whole Crude, psi"): {
        "attr": "reid_vapor_pressure",
        "unit": "Pa",
        "convert_from": "psi"
    },
    norm("Hydrogen Sulfide (dissolved), ppm"): {
        "attr": "hydrogen_sulfide_concentration",
        "unit": "ppm",
        "convert_from": "ppm"
    },
    norm("Salt content, ptb"): {
        "attr": "salt_content",
        "unit": "ppm",
        "convert_from": "ppb"
    },
    norm("Paraffins, vol %"): {
        "attr": "paraffin_volume_fraction",
        "unit": "%",
        "convert_from": "%"
    },
    norm("Naphthenes, vol %"): {
        "attr": "naphthene_volume_fraction",
        "unit": "%",
        "convert_from": "%"
    },
    norm("Aromatics (FIA), vol %"): {
        "attr": "aromatic_volume_fraction",
        "unit": "%",
        "convert_from": "%"
    },
    norm("CCR, wt%"): {
        "attr": "ccr_percent",
        "unit": "%",
        "convert_from": "%"
    },
    norm("Calcium, ppm"): {
        "attr": "calcium_mass_fraction",
        "unit": "ppm",
        "convert_from": "ppm"
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
    oil = Oil(name)
    data = iter(data)

    read_header(oil, data)
    row = next_non_empty(data)
    sample_names = row[1:]
    samples = [Sample(name=name) for name in sample_names]
    cut_table = read_cut_table(oil, data)
    apply_map(data, cut_table, samples)
    process_cut_table(oil, samples, cut_table)

    return oil


def read_header(oil, data):
    # fixme: this should probably be more flexible
    #        but we can wait 'till we get data that doesn't match
    # it could / should read the whole dist cut table, then map it
    # to the samples Exxon info in the header
    oil.reference = "\n".join([next(data)[0] for _ in range(3)])


def read_cut_table(_oil, data):

    cut_table = {}

    while True:
        try:
            row = next_non_empty(data)
            cut_table[norm(row[0])] = row[1:]
        except StopIteration:
            break
    return cut_table


def apply_map(data, cut_table, samples):
    for name, data in MAPPING.items():
        row = cut_table[name]
        set_sample_property(row, samples, **data)


def process_cut_table(oil, samples, cut_table):
    """
    process the parts that aren't a simple map
    """
    # Cut Volume
    # row = get_next_properties_row(data, "Cut volume, %")
    # Dist cuts -- each cut has part of it
    row = cut_table[norm("Cut volume, %")]
    for sample, val in zip(samples, row):
        sample.cut_volume = UnittedValue(round(val, 4), unit="%")

    # API -- odd because we only need one!
    row = cut_table[norm("API Gravity,")]
    # pull API from first value
    oil.api = round(float(row[0]), 1)  # stored as full precision double

    # use specific gravity to get density
    row = cut_table[norm("Specific Gravity (60/60F)")]
    for sample, val in zip(samples, row):
        rho = uc.convert("SG", "g/cm^3", val)
        sample.densities = [Density(UnittedValue(round(rho, 8),
                                                 unit="g/cm^3"),
                                    UnittedValue(15.6,
                                                 unit="C"))
                            ]

    # viscosity
    # fixme: -- maybe should parse the labels for temp, etc?
    #          wait till next version
    row = cut_table[norm("Viscosity at 20C/68F, cSt")]
    for sample, val in zip(samples, row):
        sample.kvis = [Viscosity(UnittedValue(round(val, 8),
                                              unit="cSt"),
                                 UnittedValue(20,
                                              unit="C"))]

    row = cut_table[norm("Viscosity at 40C/104F, cSt")]
    for sample, val in zip(samples, row):
        sample.kvis.append(Viscosity(UnittedValue(round(val, 8),
                                                  unit="cSt"),
                                     UnittedValue(40,
                                                  unit="C")))
    row = cut_table[norm("Viscosity at 50C/122F, cSt")]
    for sample, val in zip(samples, row):
        sample.kvis.append(Viscosity(UnittedValue(round(val, 8),
                                                  unit="cSt"),
                                     UnittedValue(50,
                                                  unit="C")))

    # distillation data
    if norm("Distillation type, TBP") not in cut_table:
        raise ValueError("I don't recognise this distillation data. \n"
                         'Expected: "Distillation type, TBP"')
    for name, row in cut_table.items():
        if norm("vol%, F") in name or name == norm("IBP, F"):
            # looks like a distillation cut.

            print("working with:", name)
            percent = 0.0 if "ibp" in name else float(name.split("vol")[0])
            print("percent is:", percent)
            print(row)
            for sample, val in zip(samples, row):
                if val is not None:
                    val = sigfigs(uc.convert("F", "C", val), 5)
                    sample.cuts.append(
                        DistCut(UnittedValue(percent, unit="%"),
                                UnittedValue(val, unit="C")
                                ))
    # sort them
    for sample in samples:
        sample.cuts.sort(key=lambda c: c.fraction.value)

    # "nitrogen_mass_fraction: UnittedValue"
    # "reid_vapor_pressure: UnittedValue"
    # "hydrogen_sulfide_concentration"

    oil.samples = samples

    return oil


def set_sample_property(row,
                        samples,
                        attr,
                        unit,
                        num_digits=4,
                        convert_from=None):
    """
    reads a row from the spreadsheet, and sets the sample properties

    optional rounding to "num_digits" digits
    optional converting to unit from convert_from (if the the data aren't in
    the right units)
    """
    for sample, val in zip(samples, row):
        if val is not None:
            if convert_from is not None:
                val = uc.convert(convert_from, unit, val)
            val = sigfigs(val, num_digits)
            setattr(sample, attr, UnittedValue(val, unit=unit))
# def set_sample_property(samples,
#                         attr,
#                         unit,
#                         num_digits=4,
#                         convert_from=None):
#     """
#     reads a row from the spreadsheet, and sets the sample properties

#     optional rounding to "num_digits" digits
#     optional converting to unit from convert_from (if the the data aren't in
#     the right units)
#     """
#     row = get_next_properties_row(data, name)
#     for sample, val in zip(samples, row[1:]):
#         if val is not None:
#             if convert_from is not None:
#                 val = uc.convert(convert_from, unit, val)
#             val = sigfigs(val, num_digits)
#             setattr(sample, attr, UnittedValue(val, unit=unit))


# def norm(string):
#     """
#     normalizes a string for comparing

#     so far: lower case, whitespace strip
#     trailing and leading comma strip
#     """
#     return string.strip().strip(',').lower()


# Utilities:
def empty(row):
    for c in row:
        if c is not None:
            return False
    return True


def next_non_empty(data):
    while True:
        row = next(data)
        if not empty(row):
            break
    return row


def get_next_properties_row(data, exp_field):
    row = next_non_empty(data)
    if norm(row[0]) != norm(exp_field):
        raise ValueError(f'Something wrong with data sheet: {row}, '
                         'expected: {exp_field}')
    return row


# class EnvCanadaAttributeMapper(object):
#     '''
#         A translation/conversion layer for the Environment Canada imported
#         record object.
#         This is intended to be used interchangeably with either an Environment
#         Canada record or record parser object.  Its purpose is to generate
#         named attributes that are suitable for creation of a NOAA Oil Database
#         record.
#     '''
#     top_record_properties = ('_id',
#                              'oil_id',
#                              'name',
#                              'location',
#                              'reference',
#                              'reference_date',
#                              'sample_date',
#                              'comments',
#                              'api',
#                              'product_type',
#                              'categories',
#                              'status')
#     sample_scalar_attrs = ('pour_point',
#                            'flash_point',
#                            'adhesion',
#                            'sulfur',
#                            'water',
#                            'wax_content',
#                            'benzene',
#                            'alkylated_pahs',
#                            'alkanes',
#                            'chromatography',
#                            'headspace',
#                            'biomarkers',
#                            'ccme',
#                            'ccme_f1',
#                            'ccme_f2',
#                            'ccme_tph')

#     def __init__(self, record):
#         '''
#             :param property_indexes: A lookup dictionary of property index
#                                      values.
#             :type property_indexes: A dictionary with property names as keys,
#                                     and associated index values into the data.
#         '''
#         self.record = record
#         self._status = None
#         self._categories = None

#     def get_interface_properties(self):
#         '''
#             These are all the property names that define the data in an
#             NOAA Oil Database record.
#             Our source data cannot be directly mapped to our object dict, so
#             we don't directly map any data items.  We will simply roll up
#             all the defined properties.
#         '''
#         props = set([p for p in dir(self.__class__)
#                      if isinstance(getattr(self.__class__, p),
#                                    property)])

#         return props

#     def generate_sample_id_attrs(self, sample_id):
#         attrs = {}

#         if sample_id == 0:
#             attrs['name'] = 'Fresh Oil Sample'
#             attrs['short_name'] = 'Fresh Oil'
#             attrs['fraction_weathered'] = sample_id
#             attrs['boiling_point_range'] = None
#         elif isinstance(sample_id, str):
#             attrs['name'] = sample_id
#             attrs['short_name'] = '{}...'.format(sample_id[:12])
#             attrs['fraction_weathered'] = None
#             attrs['boiling_point_range'] = None
#         elif isinstance(sample_id, Number):
#             # we will assume this is a simple fractional weathered amount
#             attrs['name'] = '{:.4g}% Weathered'.format(sample_id * 100)
#             attrs['short_name'] = '{:.4g}% Weathered'.format(sample_id * 100)
#             attrs['fraction_weathered'] = sample_id
#             attrs['boiling_point_range'] = None
#         else:
#             logger.warn("Can't generate IDs for sample: ", sample_id)

#         return attrs

#     def sort_samples(self, samples):
#         if all([s['fraction_weathered'] is not None for s in samples]):
#             return sorted(samples, key=lambda v: v['fraction_weathered'])
#         else:
#             # if we can't sort on weathered amount, then we will choose to
#             # not sort at all
#             return list(samples)

#     def dict(self):
#         rec = {}
#         samples = defaultdict(dict)

#         for p in self.get_interface_properties():
#             k, v = p, getattr(self, p)

#             if k in self.top_record_properties:
#                 rec[k] = v
#             elif hasattr(v, '__iter__') and not hasattr(v, '__len__'):
#                 # we have a sequence of items
#                 for i in v:
#                     w = i.get('weathering', 0.0)
#                     i.pop('weathering', None)

#                     if k in self.sample_scalar_attrs:
#                         samples[w][k] = i
#                     else:
#                         try:
#                             samples[w][k].append(i)
#                         except KeyError:
#                             samples[w][k] = []
#                             samples[w][k].append(i)
#             else:
#                 # assume a weathering of 0
#                 samples[0.0][k] = v

#         # MongoDB strikes again.  Apparently, in order to support their query
#         # methods, dictionary keys, for all dicts, need to be a string that
#         # contains no '$' or '.' characters.  So we cannot use a floating point
#         # number as a dict key.  So instead of a dict of samples, it will be a
#         # list of dicts that contain a sample_id.  This sample_id will not be a
#         # proper MongoDB ID, but a human-readable way to identify the sample.
#         #
#         # For NOAA Filemaker records, the ID will be the weathering amount.
#         for k, v in samples.items():
#             v.update(self.generate_sample_id_attrs(k))

#         rec['samples'] = self.sort_samples(samples.values())

#         return rec

#     def _class_path(self, class_obj):
#         return '{}.{}'.format(class_obj.__module__, class_obj.__name__)

#     def _get_kwargs(self, obj):
#         '''
#             Since we want to interchangeably use a parser or a record for our
#             source object, a common operation will be to guarantee that we are
#             always working with a kwargs struct.
#         '''
#         if isinstance(obj, dict):
#             return obj
#         else:
#             return obj.dict()

#     @property
#     def status(self):
#         '''
#             The parser does not have this, but we will want to get/set
#             this property.
#         '''
#         return self._status

#     @status.setter
#     def status(self, value):
#         self._status = value

#     @property
#     def categories(self):
#         '''
#             The parser does not have this, but we will want to get/set
#             this property.
#         '''
#         return self._categories

#     @categories.setter
#     def categories(self, value):
#         self._categories = value

#     @property
#     def name(self):
#         return self.record.name

#     @property
#     def oil_id(self):
#         return self.record.oil_id

#     @property
#     def _id(self):
#         return self.oil_id

#     @property
#     def reference(self):
#         return self.record.reference

#     @property
#     def reference_date(self):
#         return self.record.reference_date

#     @property
#     def sample_date(self):
#         return self.record.sample_date

#     @property
#     def comments(self):
#         return self.record.comments

#     @property
#     def location(self):
#         return self.record.location

#     @property
#     def product_type(self):
#         return self.record.product_type

#     @property
#     def apis(self):
#         for a in self.record.apis:
#             yield self._get_kwargs(a)

#     @property
#     def densities(self):
#         for d in self.record.densities:
#             kwargs = self._get_kwargs(d)

#             kwargs['density'] = (DensityUnit(value=kwargs['g_ml'],
#                                              from_unit='g/mL', unit='kg/m^3')
#                                  .dict())

#             kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
#                                                   from_unit='C', unit='K')
#                                   .dict())

#             del kwargs['g_ml']
#             del kwargs['ref_temp_c']

#             yield kwargs

#     @property
#     def dvis(self):
#         '''
#             the mpa_s value could be a ranged value coming from the spreadsheet
#             so it is already a dict with either a value or a (min, max) set.
#             It already has a unit set.
#         '''
#         for d in self.record.dvis:
#             kwargs = self._get_kwargs(d)

#             kwargs['mpa_s']['from_unit'] = kwargs['mpa_s']['unit']
#             kwargs['mpa_s']['unit'] = 'Pa s'
#             kwargs['viscosity'] = (DynamicViscosityUnit(**kwargs['mpa_s'])
#                                    .dict())

#             kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
#                                                   from_unit='C', unit='K')
#                                   .dict())

#             del kwargs['mpa_s']
#             del kwargs['ref_temp_c']

#             yield kwargs

#     @property
#     def kvis(self):
#         '''
#             N/A. Env. Canada records don't have this.
#         '''
#         if False:
#             yield None

#     @property
#     def ifts(self):
#         for i in self.record.ifts:
#             kwargs = self._get_kwargs(i)

#             kwargs['tension'] = (InterfacialTensionUnit(
#                                      value=kwargs['dynes_cm'],
#                                      from_unit='dyne/cm', unit='N/m')
#                                  .dict())

#             kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
#                                                   from_unit='C', unit='K')
#                                   .dict())

#             del kwargs['dynes_cm']
#             del kwargs['ref_temp_c']

#             yield kwargs

#     @property
#     def flash_point(self):
#         for f in self.record.flash_points:
#             kwargs = self._get_kwargs(f)

#             kwargs['ref_temp_c']['from_unit'] = kwargs['ref_temp_c']['unit']
#             kwargs['ref_temp_c']['unit'] = 'K'

#             kwargs['ref_temp'] = (TemperatureUnit(**kwargs['ref_temp_c'])
#                                   .dict())

#             del kwargs['ref_temp_c']

#             yield kwargs

#     @property
#     def pour_point(self):
#         for p in self.record.pour_points:
#             kwargs = self._get_kwargs(p)

#             kwargs['ref_temp_c']['from_unit'] = kwargs['ref_temp_c']['unit']
#             kwargs['ref_temp_c']['unit'] = 'K'

#             kwargs['ref_temp'] = (TemperatureUnit(**kwargs['ref_temp_c'])
#                                   .dict())

#             del kwargs['ref_temp_c']

#             yield kwargs

#     @property
#     def cuts(self):
#         for c in self.record.cuts:
#             kwargs = self._get_kwargs(c)

#             kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
#                                   '_cls': self._class_path(FloatUnit)}

#             kwargs['vapor_temp'] = (TemperatureUnit(value=kwargs['temp_c'],
#                                                     from_unit='C', unit='K')
#                                     .dict())

#             del kwargs['percent']
#             del kwargs['temp_c']

#             yield kwargs

#     @property
#     def adhesion(self):
#         for a in self.record.adhesions:
#             kwargs = self._get_kwargs(a)

#             kwargs['adhesion'] = (AdhesionUnit(value=kwargs['g_cm_2'],
#                                                from_unit='g/cm^2',
#                                                unit='N/m^2')
#                                   .dict())

#             del kwargs['g_cm_2']

#             yield kwargs

#     @property
#     def evaporation_eqs(self):
#         for e in self.record.evaporation_eqs:
#             yield self._get_kwargs(e)

#     @property
#     def emulsions(self):
#         for e in self.record.emulsions:
#             kwargs = self._get_kwargs(e)

#             kwargs['water_content'] = {
#                 'value': kwargs['water_content_percent'], 'unit': '%',
#                 '_cls': self._class_path(FloatUnit)
#             }

#             kwargs['age'] = (TimeUnit(value=kwargs['age_days'],
#                                       from_unit='day', unit='s')
#                              .dict())

#             kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
#                                                   from_unit='C', unit='K')
#                                   .dict())

#             # the different modulus values have similar units of measure
#             # to adhesion, so this is what we will go with
#             for mod_lbl in ('complex_modulus_pa',
#                             'storage_modulus_pa',
#                             'loss_modulus_pa'):
#                 value = kwargs[mod_lbl]
#                 new_lbl = mod_lbl[:-3]

#                 if value is not None:
#                     kwargs[new_lbl] = (AdhesionUnit(value=value,
#                                                     from_unit='Pa',
#                                                     unit='N/m^2')
#                                        .dict())

#             for visc_lbl in ('complex_viscosity_pa_s',):
#                 value = kwargs[visc_lbl]
#                 new_lbl = visc_lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = (DynamicViscosityUnit(value=value,
#                                                             from_unit='Pa.s',
#                                                             unit='kg/(m s)')
#                                        .dict())

#             del kwargs['water_content_percent']
#             del kwargs['age_days']
#             del kwargs['ref_temp_c']
#             del kwargs['complex_modulus_pa']
#             del kwargs['storage_modulus_pa']
#             del kwargs['loss_modulus_pa']
#             del kwargs['complex_viscosity_pa_s']

#             yield kwargs

#     @property
#     def chemical_dispersibility(self):
#         for c in self.record.corexit:
#             kwargs = self._get_kwargs(c)

#             kwargs['dispersant'] = 'Corexit 9500'
#             kwargs['effectiveness'] = kwargs['dispersant_effectiveness']
#             kwargs['effectiveness']['_cls'] = self._class_path(FloatUnit)

#             del kwargs['dispersant_effectiveness']

#             yield kwargs

#     @property
#     def sulfur(self):
#         for s in self.record.sulfur:
#             kwargs = self._get_kwargs(s)

#             kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
#                                   '_cls': self._class_path(FloatUnit)}

#             del kwargs['percent']

#             yield kwargs

#     @property
#     def water(self):
#         for w in self.record.water:
#             kwargs = self._get_kwargs(w)

#             kwargs['fraction'] = kwargs['percent']
#             kwargs['fraction']['_cls'] = self._class_path(FloatUnit)

#             del kwargs['percent']

#             yield kwargs

#     @property
#     def wax_content(self):
#         for w in self.record.wax_content:
#             kwargs = self._get_kwargs(w)

#             kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
#                                   '_cls': self._class_path(FloatUnit)}

#             del kwargs['percent']

#             yield kwargs

#     @property
#     def benzene(self):
#         for b in self.record.benzene:
#             kwargs = self._get_kwargs(b)

#             for lbl in ('benzene_ug_g',
#                         'toluene_ug_g',
#                         'ethylbenzene_ug_g',
#                         'm_p_xylene_ug_g',
#                         'o_xylene_ug_g',
#                         'isopropylbenzene_ug_g',
#                         'propylebenzene_ug_g',
#                         'isobutylbenzene_ug_g',
#                         'amylbenzene_ug_g',
#                         'n_hexylbenzene_ug_g',
#                         '_1_2_3_trimethylbenzene_ug_g',
#                         '_1_2_4_trimethylbenzene_ug_g',
#                         '_1_2_dimethyl_4_ethylbenzene_ug_g',
#                         '_1_3_5_trimethylbenzene_ug_g',
#                         '_1_methyl_2_isopropylbenzene_ug_g',
#                         '_2_ethyltoluene_ug_g',
#                         '_3_4_ethyltoluene_ug_g'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value, 'from_unit': 'ug/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             yield kwargs

#     @property
#     def headspace(self):
#         for h in self.record.headspace:
#             kwargs = self._get_kwargs(h)

#             for lbl in ('n_c5_mg_g',
#                         'n_c6_mg_g',
#                         'n_c7_mg_g',
#                         'n_c8_mg_g',
#                         'c5_group_mg_g',
#                         'c6_group_mg_g',
#                         'c7_group_mg_g'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value, 'from_unit': 'mg/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             yield kwargs

#     @property
#     def chromatography(self):
#         for c in self.record.chromatography:
#             kwargs = self._get_kwargs(c)

#             for lbl in ('tph_mg_g',
#                         'tsh_mg_g',
#                         'tah_mg_g'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value, 'unit': 'mg/g',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)}

#                 del kwargs[lbl]

#             for lbl in ('tsh_tph_percent',
#                         'tah_tph_percent',
#                         'resolved_peaks_tph_percent'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-8]

#                 if value is not None:
#                     kwargs[new_lbl] = {'value': value, 'unit': '%',
#                                        '_cls': self._class_path(FloatUnit)}

#                 del kwargs[lbl]

#             yield kwargs

#     @property
#     def ccme(self):
#         for c in self.record.ccme:
#             kwargs = self._get_kwargs(c)

#             for n in range(1, 5):
#                 lbl, new_lbl = 'f{}_mg_g'.format(n), 'f{}'.format(n)
#                 value = kwargs[lbl]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value, 'unit': 'mg/g',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             yield kwargs

#     @property
#     def ccme_f1(self):
#         for c in self.record.ccme_f1:
#             yield self._get_kwargs(c)

#     @property
#     def ccme_f2(self):
#         for c in self.record.ccme_f2:
#             yield self._get_kwargs(c)

#     @property
#     def ccme_tph(self):
#         for c in self.record.ccme_tph:
#             yield self._get_kwargs(c)

#     @property
#     def sara_total_fractions(self):
#         for f in self.record.sara_total_fractions:
#             kwargs = self._get_kwargs(f)

#             kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
#                                   '_cls': self._class_path(FloatUnit)}

#             yield kwargs

#     @property
#     def alkanes(self):
#         for a in self.record.alkanes:
#             kwargs = self._get_kwargs(a)

#             for lbl in ('pristane_ug_g', 'phytane_ug_g'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value,
#                         'from_unit': 'ug/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             for n in range(8, 45):
#                 lbl, new_lbl = 'c{}_ug_g'.format(n), 'c{}'.format(n)
#                 value = kwargs[lbl]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value,
#                         'from_unit': 'ug/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             yield kwargs

#     @property
#     def alkylated_pahs(self):
#         for a in self.record.alkylated_pahs:
#             kwargs = self._get_kwargs(a)

#             for i, g in [(i, g) for g in 'npdfbc' for i in range(5)]:
#                 lbl, new_lbl = ('c{}_{}_ug_g'.format(i, g),
#                                 'c{}_{}'.format(i, g))
#                 value = kwargs.get(lbl, None)

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value,
#                         'from_unit': 'ug/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 if lbl in kwargs:
#                     del kwargs[lbl]

#             for lbl in ('biphenyl_ug_g',
#                         'acenaphthylene_ug_g',
#                         'acenaphthene_ug_g',
#                         'anthracene_ug_g',
#                         'fluoranthene_ug_g',
#                         'pyrene_ug_g',
#                         'benz_a_anthracene_ug_g',
#                         'benzo_b_fluoranthene_ug_g',
#                         'benzo_k_fluoranthene_ug_g',
#                         'benzo_e_pyrene_ug_g',
#                         'benzo_a_pyrene_ug_g',
#                         'perylene_ug_g',
#                         'indeno_1_2_3_cd_pyrene_ug_g',
#                         'dibenzo_ah_anthracene_ug_g',
#                         'benzo_ghi_perylene_ug_g'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value,
#                         'from_unit': 'ug/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             yield kwargs

#     @property
#     def biomarkers(self):
#         for b in self.record.biomarkers:
#             kwargs = self._get_kwargs(b)

#             for lbl in ('c21_tricyclic_terpane_ug_g',
#                         'c22_tricyclic_terpane_ug_g',
#                         'c23_tricyclic_terpane_ug_g',
#                         'c24_tricyclic_terpane_ug_g',
#                         '_30_norhopane_ug_g',
#                         'hopane_ug_g',
#                         '_30_homohopane_22s_ug_g',
#                         '_30_homohopane_22r_ug_g',
#                         '_30_31_bishomohopane_22s_ug_g',
#                         '_30_31_bishomohopane_22r_ug_g',
#                         '_30_31_trishomohopane_22s_ug_g',
#                         '_30_31_trishomohopane_22r_ug_g',
#                         'tetrakishomohopane_22s_ug_g',
#                         'tetrakishomohopane_22r_ug_g',
#                         'pentakishomohopane_22s_ug_g',
#                         'pentakishomohopane_22r_ug_g',
#                         '_18a_22_29_30_trisnorneohopane_ug_g',
#                         '_17a_h_22_29_30_trisnorhopane_ug_g',
#                         '_14b_h_17b_h_20_cholestane_ug_g',
#                         '_14b_h_17b_h_20_methylcholestane_ug_g',
#                         '_14b_h_17b_h_20_ethylcholestane_ug_g'):
#                 value = kwargs[lbl]
#                 new_lbl = lbl[:-5]

#                 if value is not None:
#                     kwargs[new_lbl] = {
#                         'value': value,
#                         'from_unit': 'ug/g', 'unit': 'ppm',
#                         '_cls': self._class_path(ConcentrationInWaterUnit)
#                     }

#                 del kwargs[lbl]

#             yield kwargs
