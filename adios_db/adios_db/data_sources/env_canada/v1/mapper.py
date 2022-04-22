#!/usr/bin/env python
from math import isclose
from numbers import Number
import logging

try:
    from slugify import Slugify
    custom_slugify = Slugify(to_lower=True, separator='_')
except ImportError:
    print("You need the awesome-slugify package to run the importing code")

from adios_db.models.oil.oil import Oil
from adios_db.data_sources.mapper import MapperBase


logger = logging.getLogger(__name__)


class EnvCanadaRecordMapper(MapperBase):
    """
    A translation/conversion layer for the Environment Canada imported
    record object.
    This is intended to be used interchangeably with either an Environment
    Canada record or record parser object.  Its purpose is to generate
    named attributes that are suitable for creation of a NOAA Oil Database
    record.
    """
    def __init__(self, record):
        """
        :param record: A parsed object representing a single oil or
                       refined product.
        :type record: A record parser object.
        """
        if hasattr(record, 'dict'):
            self.record = record
        else:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'invalid parser passed in')
        self._status = None
        self._labels = []

    @property
    def oil_id(self):
        return self.record.oil_id

    @property
    def oil_labels(self):
        return self._labels

    @oil_labels.setter
    def oil_labels(self, value):
        self._labels = value

    @property
    def metadata(self):
        ret = self.record.metadata
        ret['labels'] = self.oil_labels

        return ret

    @metadata.setter
    def metadata(self, value):
        """
        Only allow the labels to be set
        """
        if 'labels' in value:
            self.oil_labels = value['labels']

    @property
    def sub_samples(self):
        return [EnvCanadaSampleMapper(s, w, c)
                for s, w, c in zip(self.record.sub_samples,
                                   self.record.weathering,
                                   self.record.ests_codes)]

    def resolve_oil_api(self, record):
        if len(record['sub_samples']) > 0:
            fresh_sample = record['sub_samples'][0]

            if ('fraction_weathered' in fresh_sample and
                    fresh_sample['fraction_weathered'] is not None and
                    not isclose(fresh_sample['fraction_weathered']['value'],
                                0.0)):
                # API cannot be determined from a non-fresh sample, even if it
                # has the data.  And since the record attributes are sparse,
                # no need to even set the API attribute
                logger.warning(f'{record["oil_id"]}: no fresh sample')
                return

            api = fresh_sample['api']

            if api is None:
                # grab the fresh density at 15C and convert
                phys = self.sub_samples[0].physical_properties
                api_densities = [d for d in phys['densities']
                                 if d['ref_temp']['unit'] == 'C'
                                 and d['ref_temp']['value'] == 15.0]
                if len(api_densities) > 0:
                    api_rho = api_densities[0]['density']['value']  # g/mL
                    api = 141.5 / api_rho - 131.5
                else:
                    logger.warning(f'oil {record["oil_id"]} '
                                   'has no API & no 15C density')
                    api = None

            if api is not None:
                record['metadata']['API'] = round(api, 2)

    def py_json(self):
        rec = self.record.dict()

        rec['sub_samples'] = [s.dict() for s in self.sub_samples]

        self.resolve_oil_api(rec)

        rec = Oil.from_py_json(rec)

        return rec.py_json()


class EnvCanadaSampleMapper(MapperBase):
    def __init__(self, parser, sample_id, ests_code):
        self.parser = parser
        self.generate_sample_id_attrs(sample_id, ests_code)

    def generate_sample_id_attrs(self, sample_id, ests_code):
        """
        :param sample_id: The value we will use to internally identify
                          a sample.  This will be mapped to metadata.name
        :param ests_code: This is the identifier that Env Canada uses for oil
                          samples. This will be mapped to metadata.sample_id
        """
        m = {}

        if sample_id == 0:
            m['name'] = 'Fresh Oil Sample'
            m['short_name'] = 'Fresh Oil'
            m['fraction_weathered'] = {'value': sample_id, 'unit': 'fraction'}
        elif isinstance(sample_id, str):
            m['name'] = sample_id
            m['short_name'] = '{}...'.format(sample_id[:12])
            m['fraction_weathered'] = None
        elif isinstance(sample_id, Number):
            # we will assume this is a simple fractional weathered amount
            m['name'] = '{:.4g}% Evaporated'.format(sample_id * 100)
            m['short_name'] = '{:.4g}% Evaporated'.format(sample_id * 100)
            m['fraction_weathered'] = {'value': sample_id, 'unit': 'fraction'}
        else:
            logger.warning(f'Cannot generate IDs for sample: {sample_id}')

        m['boiling_point_range'] = None
        m['sample_id'] = str(ests_code)

        self.metadata = m

    def dict(self):
        rec = self.parser.dict()
        for attr in ('metadata',
                     'physical_properties',
                     'environmental_behavior',
                     'SARA',
                     'distillation_data',
                     'compounds',
                     'bulk_composition',
                     # 'headspace_analysis',
                     'CCME',
                     'ESTS_hydrocarbon_fractions'):
            rec[attr] = getattr(self, attr)

        return rec

    def __getattr__(self, name):
        """
        anything we don't explicitly define should fall through here
        """
        return getattr(self.parser, name)

    @property
    def densities(self):
        ret = self.transpose_dict_of_lists(self.parser.densities)

        for item in ret:
            item['density'] = {
                'value': item.pop('density'),
                'unit': item.pop('unit'),
                'standard_deviation': item.pop('standard_deviation'),
                'replicates': item.pop('replicates')
            }

        return sorted([r for r in ret if r['density']['value'] is not None],
                      key=lambda x: x['ref_temp']['value'])

    @property
    def dynamic_viscosities(self):
        ret = self.transpose_dict_of_lists(self.parser.dvis)

        for item in ret:
            item['viscosity'] = {
                'value': item.pop('viscosity'),
                'unit': item.pop('unit'),
                'standard_deviation': item.pop('standard_deviation'),
                'replicates': item.pop('replicates')
            }

            item['method'] = self.prepend_ests(item['method'])

            value, unit = item['condition'].split()[-2:]

            if unit == '1/s':
                try:
                    value = float(value.split('=')[1])
                except IndexError:
                    value = float(value)

                item['shear_rate'] = {'value': value, 'unit': unit}

            item.pop('condition')

        return sorted([r for r in ret if r['viscosity']['value'] is not None],
                      key=lambda x: x['ref_temp']['value'])

    @property
    def distillation_data(self):
        ret = {}
        cuts = []

        # First the boiling point distribution data (if present)
        for frac in list(range(5, 101, 5)) + ['initial_boiling_point']:
            if frac == 100:
                frac_lbl = self.parser.slugify('1')
            elif isinstance(frac, Number):
                frac_lbl = self.parser.slugify(f'{frac / 100.0}')
            else:
                frac_lbl = frac

            ref_temp = self.parser.boiling_point_distribution[frac_lbl]

            if frac == 'initial_boiling_point':
                frac = 0.0

            if ref_temp is not None:
                cuts.append({
                    'fraction': self.measurement(frac, '%',
                                                 unit_type='massfraction'),
                    'vapor_temp': self.measurement(ref_temp, 'C')
                })

        # Then the cumulative weight fraction (if present)
        for ref_temp in list(range(40, 201, 20)) + list(range(250, 701, 50)):
            temp_lbl = self.parser.slugify(str(ref_temp))
            frac = self.parser.boiling_point_cumulative_fraction[temp_lbl]

            if frac is not None:
                cuts.append({
                    'fraction': self.measurement(frac, '%'),
                    'vapor_temp': self.measurement(ref_temp, 'C')
                })

        # Based on the data in the spreadsheet, fbp is somewhere between the
        # 95% temperature and the 100% temperature, but we can't determine
        # the fraction.  So we assign it to the end_point attribute, similar
        # to the Exxon data.
        ret['end_point'] = self.measurement(
            self.parser.boiling_point_distribution['fbp'], 'C'
        )

        ret['method'] = self.parser.boiling_point_distribution['method']
        if ret['method'] is None:
            ret['method'] = (self.parser
                             .boiling_point_cumulative_fraction['method'])

        ret['type'] = 'mass fraction'
        ret['cuts'] = cuts

        return ret

    @property
    def flash_point(self):
        ret = {}
        fp = dict(self.parser.flash_point.items())

        value = self.min_max(fp.pop('flash_point', None))
        if all([i is None for i in value]):
            return None

        if value[0] == value[1]:
            fp['value'] = value[0]
        else:
            fp['min_value'], fp['max_value'] = value

        fp['unit'] = 'C'
        ret['method'] = fp.pop('method', None)
        ret['measurement'] = fp

        return ret

    @property
    def pour_point(self):
        ret = {}
        pp = dict(self.parser.pour_point.items())

        value = self.min_max(pp.pop('pour_point', None))
        if all([i is None for i in value]):
            return None

        if value[0] == value[1]:
            pp['value'] = value[0]
        else:
            pp['min_value'], pp['max_value'] = value

        pp['unit'] = 'C'
        ret['method'] = pp.pop('method', None)
        ret['measurement'] = pp

        return ret

    @property
    def interfacial_tensions(self):
        ret = self.transpose_dict_of_lists(self.parser.ifts)

        for item in ret:
            if_map = {
                'Oil/ air interface': 'air',
                'Oil/water interface': 'water',
                'Oil/salt water, 3.3% NaCl interface': 'seawater'
            }
            item['interface'] = if_map[item['interface']]

            item['tension'] = {
                'value': item.pop('interfacial_tension'),
                'unit': item.pop('unit'),
                'standard_deviation': item.pop('standard_deviation'),
                'replicates': item.pop('replicates')
            }

            item['method'] = self.prepend_ests(item['method'])

        return [r for r in ret if r['tension']['value'] is not None]

    @property
    def interfacial_tension_air(self):
        ret = list(filter(lambda t: t['interface'] == 'air',
                          self.interfacial_tensions))

        for r in ret:
            r.pop('interface')

        return ret

    @property
    def interfacial_tension_water(self):
        ret = list(filter(lambda t: t['interface'] == 'water',
                          self.interfacial_tensions))

        for r in ret:
            r.pop('interface')

        return ret

    @property
    def interfacial_tension_seawater(self):
        ret = list(filter(lambda t: t['interface'] == 'seawater',
                          self.interfacial_tensions))

        for r in ret:
            r.pop('interface')

        return ret

    @property
    def dispersibilities(self):
        value = self.parser.chemical_dispersibility['dispersant_effectiveness']

        if value is not None:
            ret = dict(self.parser.chemical_dispersibility.items())

            ret['dispersant'] = 'Corexit 9500'
            ret['method'] = 'Swirling Flask Test (ASTM F2059)'
            ret.pop('dispersant_effectiveness', None)

            ret.update([
                ('effectiveness', self.measurement(
                     value, '%',
                     standard_deviation=ret.pop('standard_deviation', None),
                     replicates=ret.pop('replicates', None)
                 ))
            ])

            return [ret]
        else:
            return []

    @property
    def emulsions(self):
        ret = []

        age_map = {'On the day of formation': 0,
                   'One week after formation': 7}

        emulsions = self.parser.emulsions
        replicates = emulsions.pop('replicates')
        std_dev = emulsions.pop('standard_deviation')
        conditions = emulsions.pop('conditions')

        # need corresponding lists of:
        # - emulsion
        # - condition
        # - standard deviation
        # - replicates
        emulsions = self.transpose_dict_of_lists(emulsions)
        conditions = self.transpose_dict_of_lists(conditions)

        n = 6  # the stride of our measurement lists
        std_dev = [std_dev[i:i + n] for i in range(0, len(std_dev), n)]
        replicates = [replicates[i:i + n]
                      for i in range(0, len(replicates), n)]

        for idx, (emul, cond, dev, repl) in enumerate(zip(emulsions,
                                                          conditions,
                                                          std_dev,
                                                          replicates)):
            ret.append({})

            ret[idx]['method'] = self.prepend_ests(emul['method'])
            ret[idx]['visual_stability'] = emul['emulsion_visual_stability']

            ret[idx]['age'] = {
                'unit': 'day',
                'value': age_map[
                    cond['emulsion_visual_stability']['condition']
                ]
            }

            ret[idx]['ref_temp'] = cond['emulsion_visual_stability']['ref_temp']

            for i, attr in enumerate(('emulsion_complex_modulus',
                                      'emulsion_storage_modulus',
                                      'emulsion_loss_modulus',
                                      'emulsion_tan_delta_v_e',
                                      'emulsion_complex_viscosity',
                                      'emulsion_water_content')):
                ret[idx][attr] = {}
                ret[idx][attr]['value'] = emul[attr]
                ret[idx][attr]['unit'] = cond[attr]['unit']
                ret[idx][attr]['standard_deviation'] = dev[i]
                ret[idx][attr]['replicates'] = repl[i]

                ret[idx][attr[len('emulsion_'):]] = ret[idx].pop(attr)

            for attr in ('complex_modulus',
                         'storage_modulus',
                         'loss_modulus'):
                ret[idx][attr]['unit_type'] = 'pressure'

            for attr in ('tan_delta_v_e',):
                ret[idx][attr]['unit_type'] = 'unitless'

        return ret

    @property
    def SARA(self):
        """
        Note: Each measurement appears to be associated with a method.
              However the Sara class only supports a single method as a
              first order attribute.
        """
        ret = {}
        sara_category = self.parser.sara_total_fractions

        ret['method'] = self.prepend_ests(sara_category['method'])

        for src_name, name, idx, in (('saturates', 'saturates', 0),
                                     ('aromatics', 'aromatics', 0),
                                     ('resin', 'resins', 0),
                                     ('asphaltene', 'asphaltenes', 1)):
            value = sara_category[src_name]
            std_dev = sara_category['standard_deviation'][idx]
            repl = sara_category['replicates'][idx]

            ret[name] = self.measurement(value, '%',
                                         standard_deviation=std_dev,
                                         replicates=repl)

        return ret

    @property
    def compounds(self):
        """
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
        """
        ret = []

        groups = [
            ('btex_group', None, 'µg/g', 'MassFraction', False),
            ('c4_c6_alkyl_benzenes', None, 'µg/g', 'MassFraction', False),
            ('naphthalenes', 'alkylated_aromatic_hydrocarbons', 'µg/g',
             'MassFraction', False),
            ('phenanthrenes', 'alkylated_aromatic_hydrocarbons', 'µg/g',
             'MassFraction', False),
            ('dibenzothiophenes', 'alkylated_aromatic_hydrocarbons', 'µg/g',
             'MassFraction', False),
            ('fluorenes', 'alkylated_aromatic_hydrocarbons', 'µg/g',
             'MassFraction', False),
            ('benzonaphthothiophenes', 'alkylated_aromatic_hydrocarbons',
             'µg/g', 'MassFraction', False),
            ('chrysenes', 'alkylated_aromatic_hydrocarbons', 'µg/g',
             'MassFraction', False),
            ('other_priority_pahs', 'alkylated_aromatic_hydrocarbons', 'µg/g',
             'MassFraction', True),
            ('n_alkanes', None, 'µg/g', 'MassFraction', True),
            ('biomarkers', None, 'µg/g', 'MassFraction', True),
        ]

        for group_args in groups:
            for c in self.compounds_in_group(*group_args):
                ret.append(c)

        return ret

    # @property
    # def headspace_analysis(self):
    #     ret = []
    #
    #     groups = [
    #         ('headspace_analysis', None, 'mg/g', 'MassFraction', False),
    #     ]
    #
    #     for group_args in groups:
    #         for c in self.compounds_in_group(*group_args):
    #             ret.append(c)
    #
    #     return ret

    @property
    def bulk_composition(self):
        """
        Gather up all the groups of compounds that comprise a 'bulk'
        amount and compile them into an organized list.

        Data points that are classified in bulk composition:
        - wax
        - water
        - Sulfur
        - GC-TPH
        - GC-TSH
        - GC-TAH
        - Hydrocarbon Content Ratio
        """
        ret = []

        gc_method = self.prepend_ests(
            self.parser.hydrocarbon_content_ratio['method']
        )

        for attr, map_to, unit, method in (
            ('wax_content', 'waxes', '%', None),
            ('water_content', None, '%', None),
            ('sulfur_content', None, '%', None),
            ('gc_tph', 'tph', 'mg/g', gc_method),
            ('gc_tsh', 'tsh', 'mg/g', gc_method),
            ('gc_tah', 'tah', 'mg/g', gc_method),
        ):
            label = self.parser.get_label(attr)

            if label.find('Content') >= 0:
                label = label[:label.find('Content') + len('Content')]

            value = getattr(self.parser, attr)

            if map_to is not None:
                value['value'] = value.pop(map_to, None)
            else:
                value['value'] = value.pop(attr, None)

            value['unit'] = unit
            value['unit_type'] = 'massfraction'

            if method is None and 'method' in value:
                method = self.prepend_ests(value.pop('method'))

            ret.append(self.compound(label,
                                     self.measurement(**value),
                                     method=method,
                                     sparse=True))

        # this one isn't as simple as the rest
        groups = [
            ('hydrocarbon_content_ratio', 'hydrocarbon_content_ratio',
             '%', 'MassFraction', True),
        ]

        for group_args in groups:
            for c in self.compounds_in_group(*group_args):
                ret.append(c)

        return ret

    @property
    def CCME(self):
        ret = dict(self.parser.values['ccme'].items())

        for k in list(ret.keys()):
            ret[k] = self.measurement(ret[k], 'mg/g', 'massfraction')
            ret[f'{k}'.upper()] = ret.pop(k)

        return ret

    @property
    def ESTS_hydrocarbon_fractions(self):
        ret = {}

        groups = [('saturates', 'ests_saturates'),
                  ('aromatics', 'ests_aromatics'),
                  ('GC_TPH', 'ests_tph')]

        for attr, name in groups:
            ret[attr] = list(self.compounds_in_group(name, None,
                                                     'mg/g', 'MassFraction',
                                                     False))
            for item in ret[attr]:
                item.pop('groups')

        ret['method'] = 'Hollebone, Bruce (2020) Personal communication'

        return ret

    @property
    def physical_properties(self):
        ret = {}

        for attr in ('pour_point', 'flash_point',
                     'densities', 'dynamic_viscosities',
                     'interfacial_tension_air',
                     'interfacial_tension_water',
                     'interfacial_tension_seawater'):
            ret[attr] = getattr(self, attr)

        return ret

    @property
    def environmental_behavior(self):
        ret = {}

        for attr in ('dispersibilities', 'emulsions', 'adhesion',
                     'ests_evaporation_test'):
            ret[attr] = getattr(self, attr)

        return ret

    def compounds_in_group(self, category, group_category,
                           unit, unit_type, filter_compounds=True):
        """
        :param category: The category attribute containing the data
        :param group_category: The category attribute containing the
                               group label
        :param unit: The unit.
        :param unit_type: The type of thing that the unit measures
                          (length, mass, etc.)
        :param filter: Filter only those attributes that have a suffix
                       matching the unit value.

        Example of content::

            {
                'name': '1-Methyl-2-Isopropylbenzene',
                'method': 'ESTS 2002b',
                'groups': ['C4-C6 Alkyl Benzenes', ...],
                'measurement': {
                    value: 3.4,
                    unit: 'ppm',
                    unit_type: 'massfraction',
                    replicates: 3,
                    standard_deviation: 0.1
                }
            }
        """
        cat_obj = getattr(self.parser, category)
        conditions = self.parser.get_conditions(category)

        if group_category is not None:
            group_name = self.parser.get_label(group_category)
        else:
            group_name = self.parser.get_label(category)

        method, replicates, std_dev = None, None, None

        if 'method' in cat_obj:
            method = self.prepend_ests(cat_obj['method'])

        if 'replicates' in cat_obj:
            replicates = cat_obj['replicates']

        if 'standard_deviation' in cat_obj:
            std_dev = cat_obj['standard_deviation']

        for k, v in cat_obj.items():
            if (v is not None and
                    k != 'method' and
                    (conditions[k]['unit'] == unit or
                     not filter_compounds)):
                attr_label = self.parser.get_label([category, k])

                yield self.compound(attr_label,
                                    self.measurement(v, unit, unit_type,
                                                     std_dev, replicates),
                                    method=method, groups=[group_name])

    def transpose_dict_of_lists(self, obj):
        """
        A common step with the parsed data is to convert a dict containing
        an orthoganal set of list values into a list of dicts, each dict
        having an indexed slice of the list values
        """
        ret = []

        for k, v in obj.items():
            for idx, v_i in enumerate(v):
                if len(ret) <= idx:
                    ret.append({k: v_i})
                else:
                    ret[idx][k] = v_i

        return ret

    def prepend_ests(self, method):
        try:
            if len(method.split('/')) == 3:
                return f'ESTS: {method}'
        except AttributeError:
            pass

        return method
