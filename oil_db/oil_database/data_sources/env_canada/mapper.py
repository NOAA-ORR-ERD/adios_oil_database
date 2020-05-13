#!/usr/bin/env python
from math import isclose
from numbers import Number
import logging

from slugify import Slugify

from oil_database.models.oil.oil import Oil
from ..mapper import MapperBase

custom_slugify = Slugify(to_lower=True, separator='_')

logger = logging.getLogger(__name__)


class EnvCanadaRecordMapper(MapperBase):
    '''
        A translation/conversion layer for the Environment Canada imported
        record object.
        This is intended to be used interchangeably with either an Environment
        Canada record or record parser object.  Its purpose is to generate
        named attributes that are suitable for creation of a NOAA Oil Database
        record.
    '''
    def __init__(self, record):
        '''
            :param record: A parsed object representing a single oil or
                           refined product.
            :type record: A record parser object.
        '''
        if hasattr(record, 'dict'):
            self.record = record
        else:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'invalid parser passed in')
        self._status = None
        self._labels = None

    @property
    def sub_samples(self):
        return [EnvCanadaSampleMapper(s, w)
                for s, w in zip(self.record.sub_samples,
                                self.record.weathering)]

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

            record['metadata']['API'] = api

    def py_json(self):
        rec = self.record.dict()

        rec['_id'] = rec['oil_id']
        rec['sub_samples'] = [s.dict() for s in self.sub_samples]

        self.resolve_oil_api(rec)

        rec = Oil.from_py_json(rec)

        return rec.py_json()


class EnvCanadaSampleMapper(MapperBase):
    def __init__(self, parser, sample_id):
        self.parser = parser
        self.generate_sample_id_attrs(sample_id)

    def generate_sample_id_attrs(self, sample_id):
        if sample_id == 0:
            self.name = 'Fresh Oil Sample'
            self.short_name = 'Fresh Oil'
            self.fraction_weathered = {'value': sample_id, 'unit': '1'}
            self.boiling_point_range = None
        elif isinstance(sample_id, str):
            self.name = sample_id
            self.short_name = '{}...'.format(sample_id[:12])
            self.fraction_weathered = None
            self.boiling_point_range = None
        elif isinstance(sample_id, Number):
            # we will assume this is a simple fractional weathered amount
            self.name = '{:.4g}% Weathered'.format(sample_id * 100)
            self.short_name = '{:.4g}% Weathered'.format(sample_id * 100)
            self.fraction_weathered = {'value': sample_id, 'unit': '1'}
            self.boiling_point_range = None
        else:
            logger.warning("Can't generate IDs for sample: ", sample_id)

        return self

    def dict(self):
        rec = self.parser.dict()
        for attr in ('name',
                     'short_name',
                     'fraction_weathered',
                     'boiling_point_range',
                     'physical_properties',
                     'environmental_behavior',
                     'SARA',
                     'distillation_data',
                     'compounds',
                     'bulk_composition',
                     'headspace_analysis',
                     'CCME'):
            rec[attr] = getattr(self, attr)

        return rec

    @property
    def densities(self):
        ret = []

        for item in (('density_0_c', 0.0, 1, 1),
                     ('density_5_c', 5.0, 1, 1),
                     ('density_15_c', 15.0, 0, 0)):
            rho_lbl, ref_temp, std_idx, repl_idx = item

            rho = self.parser.densities[rho_lbl]
            std_dev = self.parser.densities['standard_deviation'][std_idx]
            replicates = self.parser.densities['replicates'][repl_idx]

            if rho is not None:
                ret.append({
                    'density': self.measurement(rho, 'g/mL',
                                                standard_deviation=std_dev,
                                                replicates=replicates),
                    'ref_temp': self.measurement(ref_temp, 'C')
                })

        return ret

    @property
    def dynamic_viscosities(self):
        ret = []

        for item in (('viscosity_at_0_c', 0.0, 1, 1),
                     ('viscosity_at_5_c', 5.0, 1, 1),
                     ('viscosity_at_15_c', 15.0, 0, 0)):
            mu_lbl, ref_temp, std_idx, repl_idx = item

            mu = self.parser.dvis[mu_lbl]
            std_dev = self.parser.dvis['standard_deviation'][std_idx]
            replicates = self.parser.dvis['replicates'][repl_idx]

            if mu is not None:
                ret.append({
                    'viscosity': self.measurement(mu, 'mPa.s',
                                                  standard_deviation=std_dev,
                                                  replicates=replicates),
                    'ref_temp': self.measurement(ref_temp, 'C')
                })

        return ret

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
                    'fraction': self.measurement(frac, '%'),
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

        ret['type'] = 'mass'
        ret['method'] = self.parser.boiling_point_cumulative_fraction['method']
        ret['cuts'] = cuts

        return ret

    @property
    def flash_point(self):
        fp = dict(self.parser.flash_point.items())

        value = self.min_max(fp.pop('flash_point', None))
        if all([i is None for i in value]):
            return None

        if value[0] == value[1]:
            fp['value'] = value[0]
        else:
            fp['min_value'], fp['max_value'] = value

        fp['unit'] = 'C'
        fp.pop('method', None)

        return fp

    @property
    def pour_point(self):
        pp = dict(self.parser.pour_point.items())

        value = self.min_max(pp.pop('pour_point', None))
        if all([i is None for i in value]):
            return None

        if value[0] == value[1]:
            pp['value'] = value[0]
        else:
            pp['min_value'], pp['max_value'] = value

        pp['unit'] = 'C'
        pp.pop('method', None)

        return pp

    @property
    def interfacial_tensions(self):
        ret = []
        method = self.parser.ifts['method']

        for intf, temp, std_idx, method_idx in (('air',       0.0, 3, 1),
                                                ('water',     0.0, 4, 1),
                                                ('seawater',  0.0, 5, 1),
                                                ('air',       5.0, 3, 1),
                                                ('water',     5.0, 4, 1),
                                                ('seawater',  5.0, 5, 1),
                                                ('air',      15.0, 0, 0),
                                                ('water',    15.0, 1, 0),
                                                ('seawater', 15.0, 2, 0)):
            lbl = f'ift_{int(temp)}_c_oil_{intf}'
            value = self.parser.ifts[lbl]

            if value is not None:
                std_dev = self.parser.ifts['standard_deviation'][std_idx]
                repl = self.parser.ifts['replicates'][std_idx]

                ret.append({
                    'interface': intf,
                    'tension': self.measurement(value, 'mN/m',
                                                standard_deviation=std_dev,
                                                replicates=repl),
                    'ref_temp': self.measurement(temp, 'C'),
                    'method': method[method_idx]
                })

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
        for e in self.parser.emulsions:
            emul = dict(e.items())

            for long_name, name, unit, std_idx, repl_idx in (
                ('complex_modulus_pa', 'complex_modulus', 'Pa', 0, 0),
                ('storage_modulus_pa', 'storage_modulus', 'Pa', 1, 0),
                ('loss_modulus_pa', 'loss_modulus', 'Pa', 2, 0),
                ('tan_delta_v_e', 'tan_delta', '%', 3, 0),
                ('complex_viscosity_pa_s', 'complex_viscosity', 'Pa.s', 4, 0),
                ('water_content_w_w', 'water_content', '%', 5, 1),
            ):
                emul.update([
                    (name, self.measurement(
                        emul.pop(long_name, None), unit,
                        standard_deviation=emul['standard_deviation'][std_idx],
                        replicates=emul['replicates'][repl_idx]
                     ))
                ])

            emul.pop('standard_deviation', None)
            emul.pop('replicates', None)
            emul['age'] = {'value': emul['age'], 'unit': 'day'}
            emul['method'] = 'ESTS 1998-2'

            ret.append(emul)

        return ret

    @property
    def SARA(self):
        '''
            Note: Each measurement appears to be associated with a method.
                  However the Sara class only supports a single method as a
                  first order attribute.
        '''
        ret = {}
        sara_category = self.parser.sara_total_fractions

        ret['method'] = ', '.join([i for i in sara_category['method']
                                   if i is not None])

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
        '''
        ret = []

        groups = [
            ('benzene', None, 'ug/g', 'Mass Fraction', False),
            ('btex_group', None, 'ug/g', 'Mass Fraction', False),
            ('c4_c6_alkyl_benzenes', None, 'ug/g', 'Mass Fraction', False),
            ('naphthalenes', 'alkylated_total_pahs', 'ug/g', 'Mass Fraction',
             False),
            ('phenanthrenes', 'alkylated_total_pahs', 'ug/g', 'Mass Fraction',
             False),
            ('dibenzothiophenes', 'alkylated_total_pahs', 'ug/g',
             'Mass Fraction', False),
            ('fluorenes', 'alkylated_total_pahs', 'ug/g', 'Mass Fraction',
             False),
            ('benzonaphthothiophenes', 'alkylated_total_pahs', 'ug/g',
             'Mass Fraction', False),
            ('chrysenes', 'alkylated_total_pahs', 'ug/g', 'Mass Fraction',
             False),
            ('other_priority_pahs', 'alkylated_total_pahs', 'ug/g',
             'Mass Fraction', False),
            ('n_alkanes', None, 'ug/g', 'Mass Fraction', False),
            ('biomarkers', None, 'ug/g', 'Mass Fraction', False),
        ]

        for group_args in groups:
            for c in self.compounds_in_group(*group_args):
                ret.append(c)

        return ret

    @property
    def headspace_analysis(self):
        ret = []

        groups = [
            ('headspace_analysis', None, 'mg/g', 'Mass Fraction', False),
        ]

        for group_args in groups:
            for c in self.compounds_in_group(*group_args):
                ret.append(c)

        return ret

    @property
    def bulk_composition(self):
        '''
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
        '''
        ret = []

        for attr, map_to, unit, method in (
            ('wax_content', 'waxes', '%', 'ESTS 1994'),
            ('water_content', None, '%', 'ASTM E203'),
            ('sulfur_content', None, '%', 'ASTM D4294'),
            ('gc_total_petroleum_hydrocarbon', 'tph', 'mg/g', 'ESTS 2002a'),
            ('gc_total_saturate_hydrocarbon', 'tsh', 'mg/g', 'ESTS 2002a'),
            ('gc_total_aromatic_hydrocarbon', 'tah', 'mg/g', 'ESTS 2002a'),
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

            ret.append(self.compound(label,
                                     self.measurement(**value),
                                     method=method,
                                     sparse=True))

        # this one isn't as simple as the rest
        groups = [
            ('hydrocarbon_content_ratio', 'hydrocarbon_content_ratio',
             '%', 'Mass Fraction', False),
        ]

        for group_args in groups:
            for c in self.compounds_in_group(*group_args):
                ret.append(c)

        return ret

    @property
    def CCME(self):
        ret = dict(self.parser.values['ccme_fractions'].items())

        for k in list(ret.keys()):
            ret[k] = self.measurement(ret[k], 'mg/g', 'massfraction')
            ret[f'ccme_{k}'.upper()] = ret.pop(k)

        ret['total_GC_TPH'] = self.measurement(
            self.parser.deep_get('gc_tph_f1_plus_f2'
                                 '.total_tph_gc_detected_tph_undetected_tph'),
            'mg/g',
            'massfraction'
        )

        groups = [
            ('saturates', 'ccme_f1'),
            ('aromatics', 'ccme_f2'),
            ('GC_TPH', 'ccme_tph'),
        ]

        for attr, name in groups:
            ret[attr] = list(self.compounds_in_group(name, None,
                                                     'mg/g', 'Mass Fraction',
                                                     False))

        ret['GC_TPH'] = [c for c in ret['GC_TPH']
                         if not c['name'].startswith('TOTAL TPH ')]

        return ret

    @property
    def physical_properties(self):
        ret = {}

        for attr in ('pour_point', 'flash_point',
                     'densities', 'dynamic_viscosities',
                     'interfacial_tensions'):
            ret[attr] = getattr(self, attr)

        return ret

    @property
    def environmental_behavior(self):
        ret = {}

        for attr in ('dispersibilities', 'emulsions'):
            ret[attr] = getattr(self, attr)

        return ret

    def compounds_in_group(self, category, group_category,
                           unit, unit_type, filter_compounds=True):
        '''
            :param category: The category attribute containing the data
            :param group_category: The category attribute containing the
                                   group label
            :param unit: The unit.
            :param unit_type: The type of thing that the unit measures
                              (length, mass, etc.)
            :param filter: Filter only those attributes that have a suffix
                           matching the unit value.

            Example of content:
                {
                    'name': "1-Methyl-2-Isopropylbenzene",
                    'method': "ESTS 2002b",
                    'groups': ["C4-C6 Alkyl Benzenes", ...],
                    'measurement': {
                        value: 3.4,
                        unit: "ppm",
                        unit_type: "Mass Fraction",
                        replicates: 3,
                        standard_deviation: 0.1
                    }
                }
        '''
        suffix = '_' + custom_slugify(unit)
        cat_obj = getattr(self.parser, category)

        if group_category is not None:
            group_name = self.parser.get_label(group_category)
        else:
            group_name = self.parser.get_label(category)

        method, replicates, std_dev = None, None, None

        if 'method' in cat_obj:
            method = cat_obj['method']

        if 'replicates' in cat_obj:
            replicates = cat_obj['replicates']

        if 'standard_deviation' in cat_obj:
            std_dev = cat_obj['standard_deviation']

        for k, v in cat_obj.items():
            if v is not None and (k.endswith(suffix) or not filter_compounds):
                attr_label = self.parser.get_label([category, k])

                yield self.compound(attr_label,
                                    self.measurement(v, unit, unit_type,
                                                     std_dev, replicates),
                                    method=method, groups=[group_name])
