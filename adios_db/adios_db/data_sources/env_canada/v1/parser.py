#!/usr/bin/env python
import re
import logging

from adios_db.util import sigfigs

from adios_db.data_sources.parser import ParserBase
from adios_db.data_sources.importer_base import (join_with, parse_time,
                                                 date_only)

logger = logging.getLogger(__name__)


# Here we map some of the more unwieldy labels to simpler ones
# These labels could appear at any level of the hierarchy
label_map = {
    'acenaphthylene_acl': 'acenaphthylene',
    'acenaphthene_ace': 'acenaphthene',
    'anthracene_an': 'anthracene',
    'benz_a_anthracene_baa': 'benz_a_anthracene',
    'benzo_a_pyrene_bap': 'benzo_a_pyrene',
    'benzo_b_fluoranthene_bbf': 'benzo_b_fluoranthene',
    'benzo_e_pyrene_bep': 'benzo_e_pyrene',
    'benzo_ghi_perylene_bgp': 'benzo_ghi_perylene',
    'benzo_k_fluoranthene_bkf': 'benzo_k_fluoranthene',
    'biphenyl_bph': 'biphenyl',
    'calculated_api_gravity': 'gravity',
    'c21_tricyclic_terpane_c21t': 'c21_tricyclic_terpane',
    'c22_tricyclic_terpane_c22t': 'c22_tricyclic_terpane',
    'c23_tricyclic_terpane_c23t': 'c23_tricyclic_terpane',
    'c24_tricyclic_terpane_c24t': 'c24_tricyclic_terpane',
    'ccme_f1': 'f1',
    'ccme_f2': 'f2',
    'ccme_f3': 'f3',
    'ccme_f4': 'f4',
    'chemical_dispersibility_swirling_flask_test': 'chemical_dispersibility',
    'dibenzo_ah_anthracene_da': 'dibenzo_ah_anthracene',
    'ests_emergencies_sciences_technologies_code': 'ests_code',
    'fluoranthene_fl': 'fluoranthene',
    'gas_chromatography_total_aromatic_hydrocarbon_gc_tah': 'tah',
    'gas_chromatography_total_petroleum_hydrocarbon_gc_tph': 'tph',
    'gas_chromatography_total_saturate_hydrocarbon_gc_tsh': 'tsh',
    'gc_tah_gc_tph': 'tah_tph',
    'gc_tsh_gc_tph': 'tsh_tph',
    'hopane_h30': 'hopane',
    'indeno_1_2_3_cd_pyrene_ip': 'indeno_1_2_3_cd_pyrene',
    'pentakishomohopane_22r_h35r': 'pentakishomohopane_22r',
    'pentakishomohopane_22s_h35s': 'pentakishomohopane_22s',
    'petroleum_hydrocarbon_fractions_ccme': 'ccme',
    'petroleum_hydrocarbon_saturates_fraction': 'ests_saturates',
    'petroleum_hydrocarbon_aromatics_fraction': 'ests_aromatics',
    'petroleum_hydrocarbon_gc_tph_saturates_aromatics_fractions': 'ests_tph',
    'pyrene_py': 'pyrene',
    'perylene_pe': 'perylene',
    'tetrakishomohopane_22r_h34r': 'tetrakishomohopane_22r',
    'tetrakishomohopane_22s_h34s': 'tetrakishomohopane_22s',
    '_18a_22_29_30_trisnorneohopane_c27ts': '_18a_22_29_30_trisnorneohopane',
    '_17a_h_22_29_30_trisnorhopane_c27tm': '_17a_h_22_29_30_trisnorhopane',
    '_14ss_h_17ss_h_20_cholestane_c27assss': '_14b_h_17b_h_20_cholestane',
    '_14ss_h_17ss_h_20_methylcholestane_c28assss': '_14b_h_17b_h_20_methylcholestane',
    '_14ss_h_17ss_h_20_ethylcholestane_c29assss': '_14b_h_17b_h_20_ethylcholestane',
    '_30_31_bishomohopane_22r_h32r': '_30_31_bishomohopane_22r',
    '_30_31_bishomohopane_22s_h32s': '_30_31_bishomohopane_22s',
    '_30_31_trishomohopane_22r_h33r': '_30_31_trishomohopane_22r',
    '_30_31_trishomohopane_22s_h33s': '_30_31_trishomohopane_22s',
    '_30_homohopane_22r_h31r': '_30_homohopane_22r',
    '_30_homohopane_22s_h31s': '_30_homohopane_22s',
    '_30_norhopane_h29': '_30_norhopane',
}


class EnvCanadaRecordParser(ParserBase):
    """
    A record class for the Environment Canada oil spreadsheet.  This is
    intended to be used with a set of data representing a single record
    from the spreadsheet.

    - We manage a hierarcical structure of properties extracted from the
      Excel columns for an oil.  Basically this will be a dictionary of
      raw property category names, where each property category itself will
      contain a dictionary of raw individual properties.

    - The data associated with any individual property will be a list of
      values corresponding to the weathered subsamples that exist for the
      oil record.
    """
    def __init__(self, values, conditions, file_props):
        """
        :param values: A dictionary of property values.
        :type values: A dictionary structure with raw property names
                      as keys, and associated values.
        :param file_props: A dictionary of property values concerning the
                           source xl spreadsheet.
        :type file_props: A dictionary structure with property names
                          as keys, and associated values.
        """
        self.values = self._slugify_keys(values)
        self.conditions = self._slugify_keys(conditions)

        self.labels = self._generate_labels(values)
        self._convert_conditions_units()

        self.file_props = file_props

    def _slugify_keys(self, obj):
        """
        Generate a structure like the incoming data, but with keys that
        have been 'slugified', which is to say turned into a string that
        is suitable for use as an object attribute.
        """
        if isinstance(obj, (tuple, list, set, frozenset)):
            return [self._slugify_keys(v)
                    for v in obj]
        elif isinstance(obj, dict):
            return dict([(label_map.get(self.slugify(k), self.slugify(k)),
                          self._slugify_keys(v))
                        for k, v in obj.items()])
        else:
            return obj

    def _generate_labels(self, obj):
        """
        Generate a structure containing the original field label data.
        - We will keep this separate from the actual data so not to make
          the data structure unnecessarily complex.
        - The hierarchy of the labels will closely match the data hierarchy
          with the following exceptions
          - The value at any particular node will be expanded to a dict
            containing:
              {'label': <raw_label>,
               'value': <value>
               }
          - This is only to contain label information.  If there is no
            expandable value at a node, it will be considered a leaf node.
            It will contain:
              {'label': <raw_label>,
               'value': None
               }
        """
        if isinstance(obj, (tuple, list, set, frozenset)):
            ret = [self._generate_labels(v) for v in obj]

            if all([i is None for i in ret]):
                ret = None

            return ret
        elif isinstance(obj, dict):
            ret = {}

            for k, v in obj.items():
                v = self._generate_labels(v)
                s_k = label_map.get(self.slugify(k), self.slugify(k))

                ret[s_k] = {'label': k,
                            'value': v}

            return ret
        else:
            return None

    def _convert_conditions_units(self, conditions=None):
        if conditions is None:
            conditions = self.conditions

        if (isinstance(conditions, dict) and
                'converted' in conditions and
                conditions['converted'] is True):
            pass
        elif isinstance(conditions, dict) and 'condition' in conditions:
            self._convert_condition(conditions)
            conditions['converted'] = True
        elif isinstance(conditions, dict):
            for _k, v in conditions.items():
                self._convert_conditions_units(v)
        elif isinstance(conditions, list):
            [self._convert_conditions_units(v)
             for v in conditions]

    def _convert_condition(self, condition):
        # ref_temp needs to be converted to Temperature type
        try:
            ref_temp, unit = re.findall(r'([0-9]+).+([CFK])',
                                        condition['ref_temp'])[0]
            ref_temp = sigfigs(ref_temp)
            condition['ref_temp'] = {'value': ref_temp, 'unit': unit}
        except (TypeError, IndexError):
            # probably encountered a None, which is fine.  We will just leave
            # it alone and move to the next one.
            pass

        # unit needs to be converted to PyNUCOS unit/unit_type
        unit_map = {
            '% w/w': ('%', 'massfraction'),
            '%w/w': ('%', 'massfraction'),
            'µg/g': ('µg/g', 'massfraction'),
            'mg/g': ('mg/g', 'massfraction'),
            'Pa.s': ('Pa.s', 'dynamicviscosity'),
            'mPa.s': ('mPa.s', 'dynamicviscosity'),
            'Pa': ('Pa', 'pressure'),
            'kPa': ('kPa', 'pressure'),
            'mN/m or dynes/cm': ('mN/m', 'interfacialtension'),
            'g/cm2': ('g/cm^2', 'needleadhesion'),
            'g/mL': ('g/mL', 'density'),
            '̊C': ('C', 'temperature'),
        }

        try:
            unit, unit_type = unit_map[condition['unit']]
            condition['unit'] = unit
            condition['unit_type'] = unit_type
        except KeyError:
            # print(f'unit key "{condition["unit"]}" not found')
            pass

    def get_label(self, nav_list):
        """
        For an attribute in our values hierarchy, get the original source
        label information.

        Ex:
            parser_obj.get_label(('gc_total_aromatic_hydrocarbon.tah'))
        """
        if isinstance(nav_list, str):
            nav_list = nav_list.split('.')

        labels = {'value': self.labels}

        for l in nav_list:
            labels = labels['value'][l]

        return labels['label']

    @property
    @join_with(' ')
    def name(self):
        """
        For now we will just concatenate all the names we see in the
        list.  In the future, we will want to be a bit smarter.
        """
        return self.values[None]['oil']

    @property
    def ests_codes(self):
        return self.values[None]['ests_code']

    @property
    def source_id(self):
        """
        We will use the ESTS codes in the record as the identifier.

        ESTS codes are a series of numbers separated by a period '.'.
        The first number in the series seems to identify the species of
        the petroleum substance, and the rest identify a degree of
        weathering.  So we will use just the first one.
        """
        primary_codes = set([str(int(str(c).split('.')[0]))
                             for c in self.ests_codes
                             if c is not None])

        assert len(primary_codes) == 1

        return primary_codes.pop()

    @property
    def oil_id(self):
        return f'EC{int(self.source_id):05}'

    @property
    def weathering(self):
        weathered_subsamples = self.values[None]['weathered']

        # this is a minor exception to the weathering.  If there is just one
        # weathered sample and it is a None value, we can probably assume
        # it is 0.0 (fresh)
        if len(weathered_subsamples) == 1 and weathered_subsamples[0] is None:
            weathered_subsamples = [0.0]
        else:
            for i, w in enumerate(weathered_subsamples):
                try:
                    weathered_subsamples[i] = float(w)
                except ValueError:
                    pass

        return weathered_subsamples

    @property
    def reference(self):
        """
        It has been decided that we will at this time use a hard-coded
        reference for all records coming from the Env. Canada datasheet.
        """
        return {
            'reference': 'Personal communication from Fatemeh Mirnaghi (ESTS)'
                         ', date: April 21, 2020.',
            'year': 2020
        }

    @property
    @date_only
    @parse_time
    def sample_date(self):
        ret = [v for v in self.values[None]['date_sample_received']
               if v is not None]

        if len(ret) > 0:
            return ret[0]
        else:
            return None

    @property
    @join_with(' ')
    def comments(self):
        return self.values[None]['comments']

    @property
    @join_with(' ')
    def location(self):
        return self.values[None]['source']

    @property
    def product_type(self):
        if self._product_type_is_probably_refined():
            return 'Refined Product NOS'
        else:
            return 'Crude Oil NOS'

    def _product_type_is_probably_refined(self):
        """
        We don't have a lot of options determining what product type the
        Env Canada records are.  The Source, Comments, and Reference fields
        might be used, but they are pretty unreliable.

        But we might be able to make some guesses based on the name of the
        product.  This is definitely not a great way to do it, but we need
        to make a determination somehow.
        """
        words = self.name.lower().split()

        for word in words:
            # if these words appear anywhere in the name, we will assume
            # it is refined
            if word in ('fuel', 'diesel', 'biodiesel',
                        'ifo', 'hfo', 'lube'):
                return True

        # check for specific n-grams of size 2
        for token in zip(words, words[1:]):
            if token in (('bunker', 'c'),
                         ('swepco', '737')):
                return True

        return False

    def vertical_slice(self, index):
        """
        All values in our self.values structure will be a list that
        conforms to the weathering subsamples for a record
        Recursively navigate values structure
        """
        return dict([(cat_key,
                      dict([(k, v[index]) for k, v in cat_val.items()]))
                     for cat_key, cat_val in self.values.items()])

    @property
    def metadata(self):
        ret = {}

        for attr in ('name',
                     'source_id',
                     'location',
                     'reference',
                     'sample_date',
                     'product_type',
                     'API',
                     'comments'):
            ret[attr] = getattr(self, attr)

        return ret

    @property
    def API(self):
        for i, w in enumerate(self.weathering):
            if w == 0.0:
                props_i = self.vertical_slice(i)

                return props_i['api_gravity']['gravity']

        # else no fresh sample
        return None

    @property
    def sub_samples(self):
        for i, w in enumerate(self.weathering):
            props_i = self.vertical_slice(i)
            props_i['weathering'] = w

            yield EnvCanadaSampleParser(props_i, self.conditions, self.labels)

    def dict(self):
        ret = {}

        for attr in ('oil_id',
                     'metadata'):
            ret[attr] = getattr(self, attr)

        ret['sub_samples'] = list(self.sub_samples)

        return ret


class EnvCanadaSampleParser(ParserBase):
    """
    A sample class for the Environment Canada oil spreadsheet.  This is
    intended to be used with a set of data representing a single subsample
    inside an oil record.

    - We manage a hierarcical structure of properties similar to that of
      the record parser

    - The data associated with any individual property will be a single
      scalar value corresponding to a weathered subsample that exists
      for an oil record.
    """
    attr_map = {
        # any attributes that are a simple mapping of the data
        'benzene': 'benzene_alkylated_benzene',
        'boiling_point_distribution': ('boiling_point_distribution_'
                                       'temperature'),
        'boiling_point_cumulative_fraction': ('boiling_point_'
                                              'cumulative_weight_fraction'),
        'ccme': 'ccme_fractions',
        'sara_total_fractions': 'hydrocarbon_group_content',
        'emulsion_complex_modulus': 'complex_modulus',
        'emulsion_complex_viscosity': 'complex_viscosity',
        'emulsion_loss_modulus': 'loss_modulus',
        'emulsion_storage_modulus': 'storage_modulus',
        'emulsion_tan_delta_v_e': 'tan_delta_v_e',
        'emulsion_visual_stability': 'visual_stability',
        'emulsion_water_content': 'water_content',
    }

    def __init__(self, values, conditions, labels):
        """
        :param values: A dictionary of property values.
        :type values: A dictionary structure with raw property names
                      as keys, and associated values.
        """
        self.values = values
        self.labels = labels
        self.conditions = conditions

    def dict(self):
        attrs = set(self.attr_map.keys())

        [attrs.add(p) for p in dir(self.__class__)
         if isinstance(getattr(self.__class__, p), property)]

        vals = []
        for a in attrs:
            try:
                vals.append((a, getattr(self, a)))
            except KeyError:
                pass

        return dict(vals)

    def deep_get(self, attr_path, default=None):
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        attrs, current = attr_path, self.values

        try:
            for p in attrs:
                current = current[p]

            return current
        except KeyError:
            return default

    def __getattr__(self, name):
        """
        The attributes are mapped to simpler names than the original
        slugified names in the datasheet.  Grab the value referenced by
        the simplified name
        """
        try:
            ret = self.values[name]
        except Exception:
            ret = self.values[self.attr_map[name]]

        return ret

    def get_label(self, nav_list):
        """
        For an attribute in our values hierarchy, get the original source
        label information.

        Ex:
            parser_obj.get_label(('gc_total_aromatic_hydrocarbon.tah'))
        """
        if isinstance(nav_list, str):
            nav_list = nav_list.split('.')

        labels = {'value': self.labels}

        for l in nav_list:
            try:
                labels = labels['value'][l]
            except KeyError:
                labels = labels['value'][self.attr_map[l]]

        return labels['label']

    def get_conditions(self, name):
        """
        The conditions object is indexed in the same way as the values.
        """
        try:
            ret = self.conditions[name]
        except Exception:
            try:
                ret = self.conditions[self.attr_map[name]]
            except Exception:
                logger.info(f'{self.__class__.__name__}.{name} not found')
                raise

        return ret

    def prepend_ests(self, method):
        try:
            if len(method.split('/')) == 3:
                return f'ESTS: {method}'
        except AttributeError:
            pass

        return method

    @property
    def api(self):
        return self.deep_get('api_gravity.gravity')

    @property
    def densities(self):
        """
        There is now a single category, density.
        Attributes within the category conform to an expected sequential
        block consisting of:
        - Density
        - Standard Deviation
        - Replicates
        - Method

        There will be 3 such blocks in the category
        """
        ret = dict(list(self.values['density'].items()))

        for attr in ('ref_temp', 'unit'):
            ret[attr] = [d[attr]
                         for d in self.conditions['density']['density']]

        return ret

    @property
    def dvis(self):
        """
        There is now a single viscosity category.

        Note: Sometimes there is a greater than ('>') indication for a
              viscosity value.  In this case, we parse the float value
              as an interval with the operator indicating whether it is
              a min or a max.
        """
        ret = dict(list(self.values['viscosity'].items()))

        for attr in ('ref_temp', 'unit', 'condition'):
            ret[attr] = [d[attr]
                         for d in self.conditions['viscosity']['viscosity']]

        return ret

    @property
    def adhesion(self):
        ret = dict(list(self.values['adhesion'].items()))

        if ret['adhesion'] is None:
            return None

        conditions = self.conditions['adhesion']['adhesion']

        ret['value'] = ret.pop('adhesion')
        ret['unit'] = conditions['unit']
        ret['unit_type'] = conditions['unit_type']
        ret['method'] = self.prepend_ests(ret['method'])

        return ret

    @property
    def ifts(self):
        """
        Now the only tricky bit is to merge the surface/interfacial tension
        attributes.
        """
        ret = dict(list(self.values['surface_interfacial_tension'].items()))
        conditions = self.conditions['surface_interfacial_tension']

        # Reconcile the surface/interfacial tensions
        # We need to order them as [sft, ift, ift, sft, ift, ift, ...]
        sfts = ret['surface_tension']
        ifts = ret['interfacial_tension']
        n = 2  # the stride of our ift list

        ret['interfacial_tension'] = []
        for sft, ift in zip(sfts,
                            [ifts[i:i + n] for i in range(0, len(ifts), n)]):
            ret['interfacial_tension'].extend([sft] + ift)

        ret.pop('surface_tension', None)

        # Now add our conditions
        # We also need to reconcile surface/interfacial here
        sfts = conditions['surface_tension']
        ifts = conditions['interfacial_tension']

        ifts_res = []
        for sft, ift in zip(sfts,
                            [ifts[i:i + n] for i in range(0, len(ifts), n)]):
            ifts_res.extend([sft] + ift)

        for attr in ('ref_temp', 'unit', 'condition'):
            ret[attr] = [
                d[attr]
                for d in ifts_res
            ]

        ret['interface'] = ret.pop('condition', None)

        return ret

    @property
    def ests_evaporation_test(self):
        ret = dict(list(self.values['evaporation_equation'].items()))

        ret['method'] = self.prepend_ests(ret['method'])

        return ret

    @property
    def emulsions(self):
        """
        The emulsions struct is more complicated in that it is a mixed bag
        of different measurements, each with their own units, temperatures,
        and age.  So we just pass the conditions as a separate attribute.
        """
        ret = dict(list(self.values['emulsion'].items()))
        ret['conditions'] = self.conditions['emulsion']

        return ret

    @property
    def chromatography(self):
        """
        The Evironment Canada data sheet contains data for gas
        chromatography analysis, which we will try to capture.

        - We have four property groups in this case, which we will merge.

          - GC-TPH
          - GC-TSH
          - GC-TAH
          - Hydrocarbon Content Ratio

        - Dimensional parameters are (weathering).

        - Values Units are split between mg/g and percent.
        """
        return dict(
            list(self.values['gc_tph'].items()) +
            list(self.values['gc_tsh'].items()) +
            list(self.values['gc_tah'].items()) +
            list(self.values['hydrocarbon_content_ratio'].items())
        )
