#!/usr/bin/env python
from numbers import Number
from collections import defaultdict
import logging

from slugify import Slugify

from oil_database.models.common.float_unit import (FloatUnit,
                                                   TemperatureUnit,
                                                   TimeUnit,
                                                   DensityUnit,
                                                   DynamicViscosityUnit,
                                                   InterfacialTensionUnit,
                                                   AdhesionUnit,
                                                   ConcentrationInWaterUnit)

custom_slugify = Slugify(to_lower=True, separator='_')

logger = logging.getLogger(__name__)


class EnvCanadaAttributeMapper(object):
    '''
        A translation/conversion layer for the Environment Canada imported
        record object.
        This is intended to be used interchangeably with either an Environment
        Canada record or record parser object.  Its purpose is to generate
        named attributes that are suitable for creation of a NOAA Oil Database
        record.
    '''
    top_record_properties = ('_id',
                             'oil_id',
                             'name',
                             'location',
                             'reference',
                             'reference_date',
                             'sample_date',
                             'comments',
                             'api',
                             'product_type',
                             'categories',
                             'status')
    sample_scalar_attrs = ('pour_point',
                           'flash_point',
                           'adhesion',
                           'sulfur',
                           'water',
                           'wax_content',
                           'benzene',
                           'alkylated_pahs',
                           'alkanes',
                           'chromatography',
                           'headspace',
                           'biomarkers',
                           'ccme',
                           'ccme_f1',
                           'ccme_f2',
                           'ccme_tph')

    def __init__(self, record):
        '''
            :param property_indexes: A lookup dictionary of property index
                                     values.
            :type property_indexes: A dictionary with property names as keys,
                                    and associated index values into the data.
        '''
        self.record = record
        self._status = None
        self._categories = None

    def get_interface_properties(self):
        '''
            These are all the property names that define the data in an
            NOAA Oil Database record.
            Our source data cannot be directly mapped to our object dict, so
            we don't directly map any data items.  We will simply roll up
            all the defined properties.
        '''
        props = set([p for p in dir(self.__class__)
                     if isinstance(getattr(self.__class__, p),
                                   property)])

        return props

    def generate_sample_id_attrs(self, sample_id):
        attrs = {}

        if sample_id == 0:
            attrs['name'] = 'Fresh Oil Sample'
            attrs['short_name'] = 'Fresh Oil'
            attrs['fraction_weathered'] = sample_id
            attrs['boiling_point_range'] = None
        elif isinstance(sample_id, str):
            attrs['name'] = sample_id
            attrs['short_name'] = '{}...'.format(sample_id[:12])
            attrs['fraction_weathered'] = None
            attrs['boiling_point_range'] = None
        elif isinstance(sample_id, Number):
            # we will assume this is a simple fractional weathered amount
            attrs['name'] = '{:.4g}% Weathered'.format(sample_id * 100)
            attrs['short_name'] = '{:.4g}% Weathered'.format(sample_id * 100)
            attrs['fraction_weathered'] = sample_id
            attrs['boiling_point_range'] = None
        else:
            logger.warn("Can't generate IDs for sample: ", sample_id)

        return attrs

    def sort_samples(self, samples):
        if all([s['fraction_weathered'] is not None for s in samples]):
            return sorted(samples, key=lambda v: v['fraction_weathered'])
        else:
            # if we can't sort on weathered amount, then we will choose to
            # not sort at all
            return list(samples)

    def dict(self):
        rec = {}
        samples = defaultdict(dict)

        for p in self.get_interface_properties():
            k, v = p, getattr(self, p)

            if k in self.top_record_properties:
                rec[k] = v
            elif hasattr(v, '__iter__') and not hasattr(v, '__len__'):
                # we have a sequence of items
                for i in v:
                    w = i.get('weathering', 0.0)
                    i.pop('weathering', None)

                    if k in self.sample_scalar_attrs:
                        samples[w][k] = i
                    else:
                        try:
                            samples[w][k].append(i)
                        except KeyError:
                            samples[w][k] = []
                            samples[w][k].append(i)
            else:
                # assume a weathering of 0
                samples[0.0][k] = v

        for k, v in samples.items():
            v.update(self.generate_sample_id_attrs(k))

        rec['samples'] = self.sort_samples(samples.values())

        return rec

    def _class_path(self, class_obj):
        return '{}.{}'.format(class_obj.__module__, class_obj.__name__)

    def _get_kwargs(self, obj):
        '''
            Since we want to interchangeably use a parser or a record for our
            source object, a common operation will be to guarantee that we are
            always working with a kwargs struct.
        '''
        return obj if isinstance(obj, dict) else obj.dict()

    @property
    def status(self):
        '''
            The parser does not have this, but we will want to get/set
            this property.
        '''
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def categories(self):
        '''
            The parser does not have this, but we will want to get/set
            this property.
        '''
        return self._categories

    @categories.setter
    def categories(self, value):
        self._categories = value

    @property
    def name(self):
        return self.record.name

    @property
    def oil_id(self):
        return self.record.oil_id

    @property
    def _id(self):
        return self.oil_id

    @property
    def reference(self):
        return self.record.reference

    @property
    def reference_date(self):
        return self.record.reference_date

    @property
    def sample_date(self):
        return self.record.sample_date

    @property
    def comments(self):
        return self.record.comments

    @property
    def location(self):
        return self.record.location

    @property
    def product_type(self):
        return self.record.product_type

    @property
    def api(self):
        '''
            This attribute is a top-level, representing the value of the
            fresh sample.
        '''
        apis = [a['gravity'] for a in self.record.apis
                if a['weathering'] == 0.0]

        try:
            return apis[0]
        except Exception:
            return None

    @property
    def apis(self):
        for a in self.record.apis:
            yield self._get_kwargs(a)

    @property
    def compounds(self):
        '''
            Gather up all the groups of compounds scattered throughout the EC
            and compile them into an organized list.

            Compounds apply to:
            - individual chemicals
            - mixed isomers

            Compounds do not apply to:
            - waxes
            - SARA
            - Sulfur
            - Carbon

            Note: Although we could in theory assign multiple groups to a
                  particular compound, we will only assign one group to the
                  list.  This group will have a close relationship to the
                  category of compounds where it is found in the EC datasheet.
            Note: Most of the compound groups don't have replicates or
                  standard deviation.  We will not add these attributes if
                  they aren't found within the attribute group.
            Todo: The measurement will be in FloatUnit types to start with.
                  Then the FloatUnit types will be enhanced to have the
                  unit_type, replicates, and standard_deviation.
        '''
        groups = [
            ('benzene_and_alkynated_benzene', None, 'ug/g', 'MassFraction'),
            ('btex_group', None, 'ug/g', 'MassFraction'),
            ('c4_c6_alkyl_benzenes', None, 'ug/g', 'MassFraction'),
            ('naphthalenes', 'alkylated_total_pahs', 'ug/g', 'MassFraction'),
            ('phenanthrenes', 'alkylated_total_pahs', 'ug/g', 'MassFraction'),
            ('dibenzothiophenes', 'alkylated_total_pahs', 'ug/g',
             'MassFraction'),
            ('fluorenes', 'alkylated_total_pahs', 'ug/g', 'MassFraction'),
            ('benzonaphthothiophenes', 'alkylated_total_pahs', 'ug/g',
             'MassFraction'),
            ('chrysenes', 'alkylated_total_pahs', 'ug/g', 'MassFraction'),
            ('other_priority_pahs', 'alkylated_total_pahs', 'ug/g',
             'MassFraction'),
            ('n_alkanes', None, 'ug/g', 'MassFraction'),
            ('biomarkers', None, 'ug/g', 'MassFraction'),
        ]

        for group_args in groups:
            for c in self.compounds_in_group(*group_args):
                yield c

    @property
    def headspace_analysis(self):
        '''
            Gather up all the headspace analysis data contained in the EC
            and compile it into an organized list.
        '''
        for c in self.compounds_in_group('headspace_analysis', None,
                                         'mg/g', 'MassFraction'):
            yield c

    def compounds_in_group(self, category, group_category, unit, unit_type):
        '''
            :param category: The category attribute containing the data
            :param group_category: The category attribute containing the
                                   group label
            :param unit: The unit
            :param unit_type: The type of thing that the unit measures
                              (length, mass, etc.)

            Example of content:
                {
                    'name': "1-Methyl-2-Isopropylbenzene",
                    'groups': ["C4-C6 Alkyl Benzenes", ...],
                    'method': "ESTS 2002b",
                    'measurement': {
                        value: 3.4,
                        unit: "ppm",
                        unit_type: "MassFraction",
                        replicates: 3,
                        standard_deviation: 0.1
                    }
                    'weathering': 0.0,  # this is not part of the spec,
                                        # and is only temporarily here to
                                        # keep track of which subsample it
                                        # belongs to.  It will be filtered out
                                        # when building the subsamples.
                }
        '''
        suffix = '_' + custom_slugify(unit)
        category_obj = getattr(self.record, category)

        if group_category is not None:
            group_name = self.record.labels[group_category]['label']
        else:
            group_name = self.record.labels[category]['label']

        for sample_obj in category_obj:
            weathering = sample_obj['weathering']
            method = None
            replicates = None
            std_dev = None

            if 'method' in sample_obj:
                method = sample_obj['method']

            if 'replicates' in sample_obj:
                replicates = sample_obj['replicates']

            if 'standard_deviation' in sample_obj:
                std_dev = sample_obj['standard_deviation']

            for k, v in sample_obj.items():
                if k.endswith(suffix) and v is not None:
                    attr_label = self.record.get_label([category,
                                                        k[:-len(suffix)]])
                    compound = {
                        'weathering': weathering,
                        'name': attr_label,
                        'groups': [group_name],
                        'method': method,
                        'measurement': {'value': v,
                                        'unit': unit,
                                        'unit_type': unit_type},
                    }

                    if replicates is not None:
                        compound['measurement']['replicates'] = replicates

                    if std_dev is not None:
                        compound['measurement']['standard_deviation'] = std_dev

                    yield compound

    @property
    def densities(self):
        for d in self.record.densities:
            kwargs = self._get_kwargs(d)

            kwargs['density'] = (DensityUnit(value=kwargs['g_ml'],
                                             from_unit='g/mL', unit='kg/m^3')
                                 .dict())

            kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
                                                  from_unit='C', unit='K')
                                  .dict())

            del kwargs['g_ml']
            del kwargs['ref_temp_c']

            yield kwargs

    @property
    def dvis(self):
        '''
            the mpa_s value could be a ranged value coming from the spreadsheet
            so it is already a dict with either a value or a (min, max) set.
            It already has a unit set.
        '''
        for d in self.record.dvis:
            kwargs = self._get_kwargs(d)

            kwargs['mpa_s']['from_unit'] = kwargs['mpa_s']['unit']
            kwargs['mpa_s']['unit'] = 'Pa s'
            kwargs['viscosity'] = (DynamicViscosityUnit(**kwargs['mpa_s'])
                                   .dict())

            kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
                                                  from_unit='C', unit='K')
                                  .dict())

            del kwargs['mpa_s']
            del kwargs['ref_temp_c']

            yield kwargs

    @property
    def kvis(self):
        '''
            N/A. Env. Canada records don't have this.
        '''
        if False:
            yield None

    @property
    def ifts(self):
        for i in self.record.ifts:
            kwargs = self._get_kwargs(i)

            kwargs['tension'] = (InterfacialTensionUnit(
                                     value=kwargs['dynes_cm'],
                                     from_unit='dyne/cm', unit='N/m')
                                 .dict())

            kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
                                                  from_unit='C', unit='K')
                                  .dict())

            del kwargs['dynes_cm']
            del kwargs['ref_temp_c']

            yield kwargs

    @property
    def flash_point(self):
        for f in self.record.flash_points:
            kwargs = self._get_kwargs(f)

            kwargs['ref_temp_c']['from_unit'] = kwargs['ref_temp_c']['unit']
            kwargs['ref_temp_c']['unit'] = 'K'

            kwargs['ref_temp'] = (TemperatureUnit(**kwargs['ref_temp_c'])
                                  .dict())

            del kwargs['ref_temp_c']

            yield kwargs

    @property
    def pour_point(self):
        for p in self.record.pour_points:
            kwargs = self._get_kwargs(p)

            kwargs['ref_temp_c']['from_unit'] = kwargs['ref_temp_c']['unit']
            kwargs['ref_temp_c']['unit'] = 'K'

            kwargs['ref_temp'] = (TemperatureUnit(**kwargs['ref_temp_c'])
                                  .dict())

            del kwargs['ref_temp_c']

            yield kwargs

    @property
    def cuts(self):
        for c in self.record.cuts:
            kwargs = self._get_kwargs(c)

            kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
                                  '_cls': self._class_path(FloatUnit)}

            kwargs['vapor_temp'] = (TemperatureUnit(value=kwargs['temp_c'],
                                                    from_unit='C', unit='K')
                                    .dict())

            del kwargs['percent']
            del kwargs['temp_c']

            yield kwargs

    @property
    def adhesion(self):
        for a in self.record.adhesions:
            kwargs = self._get_kwargs(a)

            kwargs['adhesion'] = (AdhesionUnit(value=kwargs['g_cm_2'],
                                               from_unit='g/cm^2',
                                               unit='N/m^2')
                                  .dict())

            del kwargs['g_cm_2']

            yield kwargs

    @property
    def evaporation_eqs(self):
        for e in self.record.evaporation_eqs:
            yield self._get_kwargs(e)

    @property
    def emulsions(self):
        for e in self.record.emulsions:
            kwargs = self._get_kwargs(e)

            kwargs['water_content'] = {
                'value': kwargs['water_content_percent'], 'unit': '%',
                '_cls': self._class_path(FloatUnit)
            }

            kwargs['age'] = (TimeUnit(value=kwargs['age_days'],
                                      from_unit='day', unit='s')
                             .dict())

            kwargs['ref_temp'] = (TemperatureUnit(value=kwargs['ref_temp_c'],
                                                  from_unit='C', unit='K')
                                  .dict())

            # the different modulus values have similar units of measure
            # to adhesion, so this is what we will go with
            for mod_lbl in ('complex_modulus_pa',
                            'storage_modulus_pa',
                            'loss_modulus_pa'):
                value = kwargs[mod_lbl]
                new_lbl = mod_lbl[:-3]

                if value is not None:
                    kwargs[new_lbl] = (AdhesionUnit(value=value,
                                                    from_unit='Pa',
                                                    unit='N/m^2')
                                       .dict())

            for visc_lbl in ('complex_viscosity_pa_s',):
                value = kwargs[visc_lbl]
                new_lbl = visc_lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = (DynamicViscosityUnit(value=value,
                                                            from_unit='Pa.s',
                                                            unit='kg/(m s)')
                                       .dict())

            del kwargs['water_content_percent']
            del kwargs['age_days']
            del kwargs['ref_temp_c']
            del kwargs['complex_modulus_pa']
            del kwargs['storage_modulus_pa']
            del kwargs['loss_modulus_pa']
            del kwargs['complex_viscosity_pa_s']

            yield kwargs

    @property
    def chemical_dispersibility(self):
        for c in self.record.corexit:
            kwargs = self._get_kwargs(c)

            kwargs['dispersant'] = 'Corexit 9500'
            kwargs['effectiveness'] = kwargs['dispersant_effectiveness']
            kwargs['effectiveness']['_cls'] = self._class_path(FloatUnit)

            del kwargs['dispersant_effectiveness']

            yield kwargs

    @property
    def sulfur(self):
        for s in self.record.sulfur:
            kwargs = self._get_kwargs(s)

            kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
                                  '_cls': self._class_path(FloatUnit)}

            del kwargs['percent']

            yield kwargs

    @property
    def water(self):
        for w in self.record.water:
            kwargs = self._get_kwargs(w)

            kwargs['fraction'] = kwargs['percent']
            kwargs['fraction']['_cls'] = self._class_path(FloatUnit)

            del kwargs['percent']

            yield kwargs

    @property
    def wax_content(self):
        for w in self.record.wax_content:
            kwargs = self._get_kwargs(w)

            kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
                                  '_cls': self._class_path(FloatUnit)}

            del kwargs['percent']

            yield kwargs

    @property
    def chromatography(self):
        for c in self.record.chromatography:
            kwargs = self._get_kwargs(c)

            for lbl in ('tph_mg_g',
                        'tsh_mg_g',
                        'tah_mg_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = {
                        'value': value, 'unit': 'mg/g',
                        '_cls': self._class_path(ConcentrationInWaterUnit)}

                del kwargs[lbl]

            for lbl in ('tsh_tph_percent',
                        'tah_tph_percent',
                        'resolved_peaks_tph_percent'):
                value = kwargs[lbl]
                new_lbl = lbl[:-8]

                if value is not None:
                    kwargs[new_lbl] = {'value': value, 'unit': '%',
                                       '_cls': self._class_path(FloatUnit)}

                del kwargs[lbl]

            yield kwargs

    @property
    def ccme(self):
        for c in self.record.ccme:
            kwargs = self._get_kwargs(c)

            for n in range(1, 5):
                lbl, new_lbl = 'f{}_mg_g'.format(n), 'f{}'.format(n)
                value = kwargs[lbl]

                if value is not None:
                    kwargs[new_lbl] = {
                        'value': value, 'unit': 'mg/g',
                        '_cls': self._class_path(ConcentrationInWaterUnit)
                    }

                del kwargs[lbl]

            yield kwargs

    @property
    def ccme_f1(self):
        for c in self.record.ccme_f1:
            yield self._get_kwargs(c)

    @property
    def ccme_f2(self):
        for c in self.record.ccme_f2:
            yield self._get_kwargs(c)

    @property
    def ccme_tph(self):
        for c in self.record.ccme_tph:
            yield self._get_kwargs(c)

    @property
    def sara_total_fractions(self):
        for f in self.record.sara_total_fractions:
            kwargs = self._get_kwargs(f)

            kwargs['fraction'] = {'value': kwargs['percent'], 'unit': '%',
                                  '_cls': self._class_path(FloatUnit)}

            yield kwargs
