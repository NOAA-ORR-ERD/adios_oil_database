#!/usr/bin/env python
import re
from functools import wraps
from datetime import datetime
from pytz import timezone
import logging

from slugify import Slugify

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

custom_slugify = Slugify(to_lower=True, separator='_')

logger = logging.getLogger(__name__)


# Here we map some of the more unwieldy labels to simpler ones
# These labels could appear at any level of the hierarchy
label_map = {
    'ests_emergencies_sciences_and_technologies_code': 'ests_code',
    'acenaphthylene_acl': 'acenaphthylene',
    'acenaphthene_ace': 'acenaphthene',
    'adhesion_g_cm2_ests_1996': 'adhesion',
    'alkylated_total_aromatic_hydrocarbons_pahs_ug_g_oil_ests_2002a': 'alkylated_total_pahs',
    'anthracene_an': 'anthracene',
    'aromatics_f2_ests_2002a': 'aromatics_f2',
    'benz_a_anthracene_baa': 'benz_a_anthracene',
    'benzo_a_pyrene_bap': 'benzo_a_pyrene',
    'benzo_b_fluoranthene_bbf': 'benzo_b_fluoranthene',
    'benzo_e_pyrene_bep': 'benzo_e_pyrene',
    'benzo_ghi_perylene_bgp': 'benzo_ghi_perylene',
    'benzo_k_fluoranthene_bkf': 'benzo_k_fluoranthene',
    'biphenyl_bph': 'biphenyl',
    'benzene_and_alkynated_benzene_ests_2002b': 'benzene_and_alkynated_benzene',
    'biomarkers_ug_g_ests_2002a': 'biomarkers',
    'btex_group_ug_g_ests_2002b': 'btex_group',
    'calculated_api_gravity': 'gravity',
    'c21_tricyclic_terpane_c21t': 'c21_tricyclic_terpane',
    'c22_tricyclic_terpane_c22t': 'c22_tricyclic_terpane',
    'c23_tricyclic_terpane_c23t': 'c23_tricyclic_terpane',
    'c24_tricyclic_terpane_c24t': 'c24_tricyclic_terpane',
    'c4_c6_alkyl_benzenes_ug_g_ests_2002b': 'c4_c6_alkyl_benzenes',
    'ccme_f1': 'f1',
    'ccme_f2': 'f2',
    'ccme_f3': 'f3',
    'ccme_f4': 'f4',
    'ccme_fractions_mg_g_oil_ests_2002a': 'ccme_fractions',
    'chemical_dispersibility_with_corexit_9500_dispersant_swirling_flask_test_astm_f2059': 'chemical_dispersibility_with_corexit_9500',
    'density_at_0_5_c_g_ml_astm_d5002': 'density_at_0_5_c',
    'density_at_15_c_g_ml_astm_d5002': 'density_at_15_c',
    'density_0_c_g_ml': 'density_0_c',
    'density_5_c_g_ml': 'density_5_c',
    'density_15_c_g_ml': 'density_15_c',
    'dibenzo_ah_anthracene_da': 'dibenzo_ah_anthracene',
    'emulsion_at_15_degc_on_the_day_of_formation_ests_1998_2': 'emulsion_at_15_c_day_0',
    'emulsion_at_15_degc_one_week_after_formation_ests_1998b': 'emulsion_at_15_c_day_7',
    'evaporation_ests_1998_1': 'evaporation',
    'fluoranthene_fl': 'fluoranthene',
    'gas_chromatography_total_aromatic_hydrocarbon_gc_tah': 'tah',
    'gas_chromatography_total_petroleum_hydrocarbon_gc_tph': 'tph',
    'gas_chromatography_total_satuare_hydrocarbon_gc_tsh': 'tsh',
    'gc_tah_mg_g_oil_ests_2002a': 'gc_total_aromatic_hydrocarbon',
    'gc_tah_gc_tph': 'tah_tph',
    'gc_tph_f1_f2_ests_2002a': 'gc_tph_f1_plus_f2',
    'gc_tph_mg_g_oil_ests_2002a': 'gc_total_petroleum_hydrocarbon',
    'gc_tsh_mg_g_oil_ests_2002a': 'gc_total_saturate_hydrocarbon',
    'gc_tsh_gc_tph': 'tsh_tph',
    'headspace_analysis_mg_g_oil_ests_2002b': 'headspace_analysis',
    'hopane_h30': 'hopane',
    'hydrocarbon_content_ratio_ests_2002a': 'hydrocarbon_content_ratio',
    'indeno_1_2_3_cd_pyrene_ip': 'indeno_1_2_3_cd_pyrene',
    'interfacial_tension_0_c_oil_water': 'ift_0_c_oil_water',
    'interfacial_tension_5_c_oil_water': 'ift_5_c_oil_water',
    'interfacial_tension_15_c_oil_water': 'ift_15_c_oil_water',
    'interfacial_tension_0_c_oil_salt_water_3_3_nacl': 'ift_0_c_oil_seawater',
    'interfacial_tension_5_c_oil_salt_water_3_3_nacl': 'ift_5_c_oil_seawater',
    'interfacial_tension_15_c_oil_salt_water_3_3_nacl': 'ift_15_c_oil_seawater',
    'n_alkanes_ug_g_oil_ests_2002a': 'n_alkanes',
    'other_priority_pahs_ug_g_oil': 'other_priority_pahs',
    'pentakishomohopane_22r_h35r': 'pentakishomohopane_22r',
    'pentakishomohopane_22s_h35s': 'pentakishomohopane_22s',
    'pyrene_py': 'pyrene',
    'perylene_pe': 'perylene',
    'saturates_f1_ests_2002a': 'saturates_f1',
    'sulfur_content_astm_d4294': 'sulfur_content',
    'surface_interfacial_tension_at_0_5_c_mn_m_or_dynes_cm': 'ift_at_0_5_c',
    'surface_interfacial_tension_at_15_c_mn_m_or_dynes_cm': 'ift_at_15_c',
    'surface_tension_0_c_oil_air': 'ift_0_c_oil_air',
    'surface_tension_5_c_oil_air': 'ift_5_c_oil_air',
    'surface_tension_15_c_oil_air': 'ift_15_c_oil_air',
    'tetrakishomohopane_22r_h34r': 'tetrakishomohopane_22r',
    'tetrakishomohopane_22s_h34s': 'tetrakishomohopane_22s',
    'viscosity_at_0_5_c_mpa_s': 'viscosity_at_0_5_c',
    'viscosity_at_0_c_mpa_s': 'viscosity_at_0_c',
    'viscosity_at_5_c_mpa_s': 'viscosity_at_5_c',
    'viscosity_at_15_c_mpa_s': 'viscosity_at_15_c',
    'water_content_astm_e203': 'water_content',
    'wax_content_ests_1994': 'wax_content',
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


def join_with(separator):
    '''
        Class method decorator to join a list of labels with a separator
    '''
    def wrapper(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            return separator.join([i.strip()
                                   for i in func(self, *args, **kwargs)
                                   if i is not None])

        return wrapped

    return wrapper


def parse_time(func):
    '''
        Class method decorator to parse an attribute return value as a datetime

        Note: Apparently there are a few records that just don't have
              a sample date.  So we can't really enforce the presence
              of a date here.

        Note: The date formats are all over the place here.  So the default
              datetime parsing is not sufficient.
              Some formats that I have seen:
              - MM/DD/YYYY          # most common
              - MM-DD-YYYY          # different separator
              - DD/MM/YYYY          # 7 records very clearly in this format
              - MM/YYYY             # 3 records do this
              - YYYY                # 2 records do this
              - <month name>, YYYY  # 3 records do this
              So we will:
              - Treat MM/DD/YYYY as the default
              - Allow for DD/MM/YYYY if it can be clearly determined
              - Fix the others in the file.
    '''
    def parse_single_datetime(date_str):
        datetime_pattern = re.compile(
            r'(?P<month>\d{1,2})[-/](?P<day>\d{1,2})[-/](?P<year>\d{2,4})'
            r'(?:[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'  # Optional HH:mm
            r'(?::(?P<second>\d{1,2})'  # Optional seconds
            r'(?:\.(?P<microsecond>\d{1,6})0*)?)?)?'  # Optional microseconds
            r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?\Z'  # Optional timezone
        )

        if isinstance(date_str, datetime):
            return date_str
        elif isinstance(date_str, str):
            match = re.match(datetime_pattern, date_str.strip())

            if match is not None:
                tp = {k: int(v) for k, v in match.groupdict().items()
                      if v is not None}

                if tp['month'] > 12:
                    tp['month'], tp['day'] = tp['day'], tp['month']

                return datetime(**tp)
            else:
                raise ValueError('datetime "{}" is not parsable'
                                 .format(date_str))
        else:
            return None

    def wrapper(*args, **kwargs):
        return [parse_single_datetime(dt)
                for dt in func(*args, **kwargs)]

    return wrapper


class EnvCanadaRecordParser(object):
    '''
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
    '''
    def __init__(self, values, file_props):
        '''
            :param values: A dictionary of property values
                                     values.
            :type values: A dictionary structure with raw property names
                          as keys, and associated values.
            :param file_props: A dictionary of property values concerning the
                               source xl spreadsheet.
            :type file_props: A dictionary structure with property names
                              as keys, and associated values.
        '''
        self.values = self.slugify_keys(values)
        self.labels = self.generate_labels(values)
        self.propagate_merged_cells()
        self.file_props = file_props

    def slugify(self, label):
        if label is None:
            return label

        prefix = '_' if label[0].isdigit() else ''

        return prefix + custom_slugify(label)

    def slugify_keys(self, obj):
        '''
            Generate a structure like the incoming data, but with keys that
            have been 'slugified', which is to say turned into a string that
            is suitable for use as an object attribute.
            - The strings will be snake-case, all lowercase words separated
              by underscores.
            - They will not start with a numeric digit.  If the original label
              starts with a digit, the slug will be prepended with an
              underscore ('_').
        '''
        if isinstance(obj, (tuple, list, set, frozenset)):
            return [self.slugify_keys(v)
                    for v in obj]
        elif isinstance(obj, dict):
            return dict([(label_map.get(self.slugify(k), self.slugify(k)),
                          self.slugify_keys(v))
                        for k, v in obj.items()])
        else:
            return obj

    def generate_labels(self, obj):
        '''
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
        '''
        if isinstance(obj, (tuple, list, set, frozenset)):
            ret = [self.generate_labels(v) for v in obj]

            if all([i is None for i in ret]):
                ret = None

            return ret
        elif isinstance(obj, dict):
            ret = {}

            for k, v in obj.items():
                v = self.generate_labels(v)
                s_k = label_map.get(self.slugify(k), self.slugify(k))

                ret[s_k] = {'label': k,
                            'value': v}

            return ret
        else:
            return None

    def propagate_merged_cells(self):
        '''
            Some rows within the columns of an oil are merged in the excel
            spreadsheet into one cell.  This is to imply that all columns
            should have the merged value.  But when parsing the columns,
            only the first one will have the value.
            So as a preprocessing step, we will propagate these values to all
            cells within that row

            In addition, some method fields are implied to be for multiple
            grouped categories, but the field only lies within one of the
            categories.
            So we need to copy it to the other category
        '''
        propagate = [('viscosity_at_0_5_c', 'method'),
                     ('ift_at_0_5_c', 'method'),
                     ('ift_at_15_c', 'method'),
                     ('flash_point_c', 'method'),
                     ('pour_point_c', 'method'),
                     ('boiling_point_cumulative_weight_fraction', 'method'),
                     ('hydrocarbon_group_content', 'method'),
                     ]

        for cat, attr in propagate:
            cells = self.values[cat][attr]
            if cells[0] is not None:
                self.values[cat][attr] = [cells[0] for _c in cells]

        copy_to = [('viscosity_at_0_5_c', 'method', 'viscosity_at_15_c'),
                   ('boiling_point_cumulative_weight_fraction', 'method',
                    'boiling_point_distribution_temperature_c')
                   ]

        for cat, attr, other_cat in copy_to:
            self.values[other_cat][attr] = self.values[cat][attr]

    def get_label(self, nav_list):
        '''
            For an attribute in our values hierarchy, get the original source
            label information.

            Ex:
                parser_obj.get_label(('gc_total_aromatic_hydrocarbon.gc_tah'))
        '''
        if isinstance(nav_list, str):
            nav_list = nav_list.split('.')

        labels = {'value': self.labels}

        for l in nav_list:
            labels = labels['value'][l]

        return labels['label']

    def get_interface_properties(self):
        '''
            These are all the property names that define the data in an
            Environment Canada record.
            Our source data cannot be directly mapped to our object dict, so
            we don't directly map any data items.  We will simply roll up
            all the defined properties.
        '''
        props = set([p for p in dir(self.__class__)
                     if isinstance(getattr(self.__class__, p), property)])

        return props

    @property
    @join_with(' ')
    def name(self):
        '''
            For now we will just concatenate all the names we see in the
            list.  In the future, we will want to be a bit smarter.
        '''
        return self.values[None]['oil']

    @property
    def ests_codes(self):
        return self.values[None]['ests_code']

    @property
    def oil_id(self):
        '''
            We will use the ESTS codes in the record as the identifier.

            ESTS codes are a series of numbers separated by a period '.'.
            The first number in the series seems to identify the species of
            the petroleum substance, and the rest identify a degree of
            weathering.  So we will use just the first one.
        '''
        primary_codes = set([int(str(c).split('.')[0])
                             for c in self.ests_codes])
        assert len(primary_codes) == 1

        return 'EC{:06.0f}'.format(primary_codes.pop())

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
    @join_with(' ')
    def reference(self):
        return self.values[None]['reference']

    @property
    def reference_date(self):
        '''
            The reference content can have:
            - no content:  In this case we take the created date of the
                           Excel file.
            - one year (YYYY):  In this case we parse the year as an int and
                                form a datetime with it.
            - multiple years (YYYY): In this case we use the highest numeric
                                     year (most recent) and form a datetime
                                     with it.
        '''
        occurrences = [int(n) for n in
                       re.compile(r'\d{4}').findall(self.reference)]
        if len(occurrences) == 0:
            return self.file_props['created']
        else:
            return datetime(max(occurrences), 1, 1, tzinfo=timezone('GMT'))

    @property
    @parse_time
    def sample_date(self):
        return self.values[None]['date_sample_received']

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
        if self.product_type_is_probably_refined():
            return 'refined'
        else:
            return 'crude'

    def product_type_is_probably_refined(self):
        '''
            We don't have a lot of options determining what product type the
            Env Canada records are.  The Source, Comments, and Reference fields
            might be used, but they are pretty unreliable.

            But we might be able to make some guesses based on the name of the
            product.  This is definitely not a great way to do it, but we need
            to make a determination somehow.
        '''
        words = self.name.lower().split()

        for word in words:
            # if these words appear anywhere in the name, we will assume
            # it is refined
            if word in ('fuel', 'diesel', 'biodiesel',
                        'ifo', 'hfo', 'lube'):
                return True

        # check for specific 2-word tokens
        for token in zip(words, words[1:]):
            if token in (('bunker', 'c'),
                         ('swepco', '737')):
                return True

        return False

    def iterate_weathering(self, obj):
        for i, w in enumerate(self.weathering):
            props_i = dict([(k, v[i]) for k, v in obj.items()])
            props_i['weathering'] = w

            yield props_i

    @property
    def apis(self):
        ret = []
        props = self.values['api_gravity']

        for props_i in self.iterate_weathering(props):
            if props_i['gravity'] is not None:
                ret.append(props_i)

        return ret

    @property
    def densities(self):
        '''
            Getting densities out of this datasheet is more tricky than it
            should be.  There are two categories, density at 15C, and density
            at 0/5C.  I dunno, I would have organized the data in a more
            orthogonal way.
        '''
        ret = []

        for temp in (0, 5, 15):
            ret.extend(self._get_densities_at(temp))

        return ret

    def _get_densities_at(self, ref_temp):
        ret = []
        temps = {0: '0_5',
                 5: '0_5',
                 15: '15'}
        temp_mask = [t for t in temps.keys() if t != ref_temp]
        cat_label = dict([(k, 'density_at_{}_c'.format(v))
                          for k, v in temps.items()])

        props = self.values[cat_label[ref_temp]]

        for props_i in self.iterate_weathering(props):
            add_props = {'ref_temp_c': ref_temp}
            rename_props = {'density_{}_c'.format(ref_temp): 'g_ml'}
            prune_props = ['density_{}_c'.format(t) for t in temp_mask]

            kwargs = self._build_kwargs(props_i,
                                        add_props=add_props,
                                        rename_props=rename_props,
                                        prune_props=prune_props)

            try:
                kwargs['g_ml'] = float(kwargs['g_ml'])
            except Exception:
                kwargs['g_ml'] = None

            if kwargs['g_ml'] not in (None, 0.0):
                ret.append(kwargs)

        return ret

    @property
    def dvis(self):
        '''
            Getting viscosities out of this datasheet is more tricky than it
            should be.  There are two categories, viscosity at 15C, and
            viscosity at 0/5C.  I dunno, I would have organized the data in a
            more orthogonal way.  Otherwise, the data is mostly what we expect,
            with only a few deviations.

            Note: Sometimes there is a greater than ('>') indication for a
                  viscosity value.  In this case, we parse the float value
                  as an interval with the operator indicating whether it is
                  a min or a max.
        '''
        ret = []

        for temp in (0, 5, 15):
            ret.extend(self._get_viscosities_at(temp))

        return ret

    def _get_viscosities_at(self, ref_temp):
        ret = []

        temps = {0: '0_5',
                 5: '0_5',
                 15: '15'}
        temp_mask = [t for t in temps.keys() if t != ref_temp]
        cat_label = dict([(k, 'viscosity_at_{}_c'.format(v))
                          for k, v in temps.items()])

        props = self.values[cat_label[ref_temp]]

        for props_i in self.iterate_weathering(props):
            add_props = {'ref_temp_c': ref_temp}
            rename_props = {'viscosity_at_{}_c'.format(ref_temp): 'mpa_s'}
            prune_props = ['viscosity_at_{}_c'.format(t) for t in temp_mask]

            op_and_value = {'mpa_s'}

            kwargs = self._build_kwargs(props_i,
                                        add_props=add_props,
                                        rename_props=rename_props,
                                        prune_props=prune_props,
                                        op_and_value=op_and_value)
            kwargs['mpa_s']['unit'] = 'mPa s'

            if any([(l in kwargs['mpa_s'] and
                     kwargs['mpa_s'][l] not in (None, 0.0))
                    for l in ('value', 'min_value', 'max_value')]):
                ret.append(kwargs)

        return ret

    @property
    def ifts(self):
        '''
            Getting interfacial tensions out of this datasheet is a bit tricky,
            but understandably so since we are dealing with a number of
            dimensional parameters (temperature, interface, weathering).
            There are two categories, surface/interfacial tension at 15C, and
            surface/interfacial tension at 0/5C.
            I still think it could have been organized more orthogonally.
        '''
        ifts = []
        for temp in (0, 5, 15):
            for if_type in ('air', 'water', 'seawater'):
                ifts.extend(self._get_tension_at(temp, if_type))

        return ifts

    def _get_tension_at(self, ref_temp, if_type):
        ret = []

        temps = {0: '0_5',
                 5: '0_5',
                 15: '15'}
        if_types = {'air': {'labels': ['oil_air'],
                            'idx': 0},
                    'water': {'labels': ['oil_water'],
                              'idx': 1},
                    'seawater': {'labels': ['oil_seawater'],
                                 'idx': 2}
                    }

        cat_label = dict([(k, 'ift_at_{}_c'.format(v))
                          for k, v in temps.items()])

        props = self.values[cat_label[ref_temp]]

        for props_i in self.iterate_weathering(props):
            add_props = {'ref_temp_c': ref_temp, 'interface': if_type}

            # We have a couple duplicate labels, one for each if_type
            # and they are all here contained in a list.  We need to
            # choose the right one.
            for dup_lbl in ('standard_deviation', 'replicates'):
                add_props[dup_lbl] = props_i[dup_lbl][if_types[if_type]['idx']]

            prune_props = []
            for temp in temps:
                for i in if_types:
                    if temp != ref_temp or i != if_type:
                        for k in list(props_i.keys()):
                            if all([k.find(l) >= 0
                                    for l in
                                    ['_{}'.format(temp)] + if_types[i]['labels']]):
                                prune_props.append(k)

            rename_props = {
                'ift_{}_c_oil_{}'.format(ref_temp, if_type): 'dynes_cm'
            }

            kwargs = self._build_kwargs(props_i,
                                        add_props=add_props,
                                        prune_props=prune_props,
                                        rename_props=rename_props)

            try:
                float(kwargs['dynes_cm'])
                ret.append(kwargs)
            except Exception:
                pass

        return ret

    @property
    def flash_points(self):
        ret = []
        props = self.values['flash_point_c']

        for props_i in self.iterate_weathering(props):
            kwargs = self.build_flash_point_kwargs(props_i)

            if any([(kwargs is not None and
                     k in kwargs and
                     kwargs[k] is not None)
                    for k in ('ref_temp_c',)]):
                ret.append(kwargs)

        return ret

    @property
    def pour_points(self):
        '''
            Getting the pour point is similar to Adios2 in that the values
            contain '>' and '<' symbols.  This indicates we need to interpret
            the content to come up with minimum and maximum values.
            Dimensional parameters are simply (weathering).
        '''
        ret = []
        props = self.values['pour_point_c']

        for props_i in self.iterate_weathering(props):
            kwargs = self._build_pour_point_kwargs(props_i)

            if any([(kwargs is not None and
                     k in kwargs and
                     kwargs[k] is not None)
                    for k in ('ref_temp_c',)]):
                ret.append(kwargs)

        return ret

    @property
    def cuts(self):
        '''
            There are two distinct sets of distillation cut data in the EC
            spreadsheet. They are:
            - Boiling Point: Distribution, Temperature (C).
              Here the labels are percent values representing the fraction
              boiled off, and the data is the temperature at which the
              fractional value occurs.
            - Boiling Point: Cumulative Weight Fraction (%).
              Here the labels are temperature (C) values, and the data is the
              fraction that is boiled off at that temperature.

            We will try to get both sets of data and then merge them if
            possible.  Most oils will have either one set or the other,
            not both.  Dimensional parameters are simply (weathering).
        '''
        cuts = self._get_cuts_from_bp_cumulative_frac()
        cuts.extend(self._get_cuts_from_bp_distribution())

        return cuts

    def _get_cuts_from_bp_distribution(self):
        cuts = []
        props = self.values['boiling_point_distribution_temperature_c']

        for props_i in self.iterate_weathering(props):
            cuts.extend(self._build_cuts_from_dist_data(props_i))

        return cuts

    def _build_cuts_from_dist_data(self, props):
        '''
            Build a list of EC distillation cut objects from boiling point
            distribution data.
            - prop_names: The list of property names
            - values: A list of Excel cell objects representing the properties.
            - weathering: The fractional oil weathering amount.

            Note: The labels have a bit of a problem.  Most of them are percent
                  value labels, which is fine, but additionally, we have
                  'initial_boiling_point', and 'fbp'.  These are unusable
                  because there is no indication of what fraction the initial
                  and final boiling point has.  I could assume the initial
                  boiling point has a fraction of 0%, but it is clear that the
                  final boiling point is a temperature somewhere between the
                  95% and 100% temperatures. So it is a fraction somewhere
                  between 95% and 100%, which we don't precisely know.
        '''
        cuts = []
        dist_data = props

        # The only labels we care about are the percent value labels
        for percent in range(5, 101, 5):
            weathering = dist_data['weathering']
            label = self.slugify('{:0.02g}'.format(percent / 100.0))
            vapor_temp_c = dist_data[label]
            method = dist_data['method']

            if vapor_temp_c is not None:
                cuts.append(self._build_cut_kwargs(vapor_temp_c, percent,
                                                   weathering, method))

        return cuts

    def _get_cuts_from_bp_cumulative_frac(self):
        cuts = []

        props = self.values['boiling_point_cumulative_weight_fraction']

        for props_i in self.iterate_weathering(props):
            cuts.extend(self._build_cuts_from_cumulative_fraction(props_i))

        return cuts

    def _build_cuts_from_cumulative_fraction(self, props):
        '''
            Build a list of EC distillation cut objects from cumulative weight
            fraction data.
            - prop_names: The list of property names
            - values: A list of Excel cell objects representing the properties.
            - weathering: The fractional oil weathering amount.

            Note: The labels have a bit of a problem.  Most of them are percent
                  value labels, which is fine, but additionally, we have
                  'initial_boiling_point', and 'fbp'.  These are unusable
                  because there is no indication of what fraction the initial
                  and final boiling point has.  I could assume the initial
                  boiling point has a fraction of 0%, but it is clear that
                  the final boiling point is a temperature somewhere between
                  the 95% and 100% temperatures. So it is a fraction somewhere
                  between 95% and 100%, which we don't precisely know.
        '''
        cuts = []
        frac_data = props

        # The only labels we care about are the temperature labels
        temp_values = list(range(40, 200, 20)) + list(range(200, 701, 50))

        for temp_c in temp_values:
            weathering = frac_data['weathering']
            label = '_{}'.format(temp_c)
            percent = frac_data[label]
            method = frac_data['method']

            if percent is not None:
                cuts.append(self._build_cut_kwargs(temp_c, percent,
                                                   weathering, method))

        return cuts

    def _build_cut_kwargs(self, vapor_temp_c, percent,
                          weathering, method):
        return {'temp_c': vapor_temp_c,
                'percent': percent,
                'weathering': weathering,
                'method': method}

    @property
    def adhesions(self):
        '''
            Dimensional parameters are simply (weathering).
        '''
        ret = []

        for props_i in self.iterate_weathering(self.values['adhesion']):
            if props_i['adhesion'] is not None:
                ret.append(self._build_kwargs(
                    props_i,
                    rename_props={'adhesion': 'g_cm_2'}
                ))

        return ret

    @property
    def evaporation_eqs(self):
        '''
            The Evironment Canada data sheet contains equations for evaporative
            loss, along with coefficient values to be used per oil. There are
            three equations and three possible coefficients (A, B, and
            optionally C). We will try to capture both the algorithm and
            the coefficients.  Dimensional parameters are simply (weathering).
        '''
        evaporation = self._get_evaporation_eqs_ests_1998()
        evaporation.extend(self._get_evaporation_eqs_mass_loss1())
        evaporation.extend(self._get_evaporation_eqs_mass_loss2())

        return evaporation

    def _get_evaporation_eqs_ests_1998(self):
        ret = []

        props = self.values['evaporation']

        for props_i in self.iterate_weathering(props):
            ret.append(self._build_evaporation_kwargs(props_i,
                                                      '(A + BT) ln t',
                                                      'for_ev_a_bt_ln_t'))

        return [eq for eq in ret
                if eq['a'] is not None and eq['b'] is not None]

    def _get_evaporation_eqs_mass_loss1(self):
        ret = []

        props = self.values['parameters_for_evaporation_equation_mass_loss']

        for props_i in self.iterate_weathering(props):
            ret.append(self._build_evaporation_kwargs(props_i,
                                                      '(A + BT) sqrt(t)',
                                                      'for_ev_a_bt_sqrt_t'))

        return [eq for eq in ret
                if eq['a'] is not None and eq['b'] is not None]

    def _get_evaporation_eqs_mass_loss2(self):
        ret = []

        props = self.values['parameters_for_evaporation_equation_mass_loss']

        for props_i in self.iterate_weathering(props):
            ret.append(self._build_evaporation_kwargs(props_i,
                                                      'A + B ln (t + C)',
                                                      'for_ev_a_b_ln_t_c'))

        return [eq for eq in ret
                if eq['a'] is not None and eq['b'] is not None]

    @property
    def emulsions(self):
        '''
            The Evironment Canada data sheet contains data for emulsion
            properties, which we will try to capture.
            Dimensional parameters are (temperature, age, weathering).
        '''
        emulsions = []

        for age in (0, 7):
            emulsions.extend(self._get_emulsion_at(age))

        return emulsions

    def _get_emulsion_at(self, age):
        emulsions = []
        props = self.values['emulsion_at_15_c_day_{}'.format(age)]

        for props_i in self.iterate_weathering(props):
            if props_i['water_content_w_w'] is not None:
                add_props = {'ref_temp_c': 15.0, 'age_days': age}
                rename_props = {'water_content_w_w': 'water_content_percent'}
                prune_props = {'standard_deviation', 'replicates'}

                sd_types = ('cm', 'sm', 'lm', 'td', 'cv', 'wc')
                for idx, sd_type in enumerate(sd_types):
                    sd_label = '{}_standard_deviation'.format(sd_type)
                    add_props[sd_label] = props_i['standard_deviation'][idx]

                add_props['mod_replicates'] = props_i['replicates'][0]
                add_props['wc_replicates'] = props_i['replicates'][1]

                kwargs = self._build_kwargs(props_i,
                                            add_props=add_props,
                                            rename_props=rename_props,
                                            prune_props=prune_props)

                emulsions.append(kwargs)

        return emulsions

    @property
    def corexit(self):
        '''
            The Evironment Canada data sheet contains data for chemical
            dispersability with Corexit 9500, which we will try to capture.
            Dimensional parameters are (weathering).
        '''
        corexit = []
        props = self.values['chemical_dispersibility_with_corexit_9500']

        for props_i in self.iterate_weathering(props):
            if props_i['dispersant_effectiveness'] is not None:
                op_and_value = {'dispersant_effectiveness'}

                kwargs = self._build_kwargs(props_i,
                                            op_and_value=op_and_value)
                kwargs['dispersant_effectiveness']['unit'] = '%'

                corexit.append(kwargs)

        return corexit

    @property
    def sulfur(self):
        '''
            Dimensional parameters are (weathering).
        '''
        sulfur_contents = []

        for props_i in self.iterate_weathering(self.values['sulfur_content']):
            if props_i['sulfur_content'] is not None:
                rename_props = {'sulfur_content': 'percent'}

                kwargs = self._build_kwargs(props_i,
                                            rename_props=rename_props)

                sulfur_contents.append(kwargs)

        return sulfur_contents

    @property
    def water(self):
        '''
            Dimensional parameters are (weathering).
        '''
        water_contents = []

        for props_i in self.iterate_weathering(self.values['water_content']):
            if props_i['water_content'] is not None:
                rename_props = {'water_content': 'percent'}
                op_and_value = {'percent'}

                kwargs = self._build_kwargs(props_i,
                                            rename_props=rename_props,
                                            op_and_value=op_and_value)
                kwargs['percent']['unit'] = '%'

                water_contents.append(kwargs)

        return water_contents

    @property
    def wax_content(self):
        '''
            Dimensional parameters are (weathering).
        '''
        wax_contents = []

        for props_i in self.iterate_weathering(self.values['wax_content']):
            if props_i['waxes'] is not None:
                add_props = {'method': 'ESTS 1994'}
                rename_props = {'waxes': 'percent'}

                kwargs = self._build_kwargs(props_i,
                                            add_props=add_props,
                                            rename_props=rename_props)

                wax_contents.append(kwargs)

        return wax_contents

    @property
    def sara_total_fractions(self):
        '''
            Dimensional parameters are (weathering).
        '''
        fractions = []

        for sara_type in ('saturates', 'aromatics', 'resin', 'asphaltene'):
            fractions.extend(self._get_sara_fractions_as(sara_type))

        return fractions

    def _get_sara_fractions_as(self, sara_type):
        sara_types = {'saturates': {'test_set': 0, 'label': 'Saturates'},
                      'aromatics': {'test_set': 0, 'label': 'Aromatics'},
                      'resin': {'test_set': 0, 'label': 'Resins'},
                      'asphaltene': {'test_set': 1, 'label': 'Asphaltenes'},
                      }

        sara_mask = [a for a in sara_types if a != sara_type]

        ret = []

        props = self.values['hydrocarbon_group_content']

        for props_i in self.iterate_weathering(props):
            if props_i[sara_type] is not None:
                sd, r, m = [props_i[label][sara_types[sara_type]['test_set']]
                            for label in ('standard_deviation',
                                          'replicates',
                                          'method')]

                add_props = {'sara_type': sara_types[sara_type]['label'],
                             'standard_deviation': sd,
                             'replicates': r,
                             'method': m}
                rename_props = {sara_type: 'percent'}
                prune_props = sara_mask

                kwargs = self._build_kwargs(props_i,
                                            add_props=add_props,
                                            prune_props=prune_props,
                                            rename_props=rename_props)

                ret.append(kwargs)

        return ret

    @property
    def benzene(self):
        '''
            The Evironment Canada data sheet contains data for Benzene content,
            which we will try to capture.
            We have 3 property groups in this case, and I think it would be ok
            to merge them into a single object.
            - Dimensional parameters are (weathering).
            - Units are all ug/g as far as I can tell.
        '''
        return self.weathering_sliced_obj(('benzene_and_alkynated_benzene',
                                           'btex_group',
                                           'c4_c6_alkyl_benzenes'),
                                          suffix='_ug_g',
                                          method='ESTS 2002b')

    @property
    def headspace(self):
        '''
            The Evironment Canada data sheet contains data for headspace
            analysis, which we will try to capture.
            We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are all mg/g as far as I can tell.
        '''
        return self.weathering_sliced_obj('headspace_analysis',
                                          suffix='_mg_g',
                                          method='ESTS 2002b')

    @property
    def chromatography(self):
        '''
            The Evironment Canada data sheet contains data for gas
            chromatography analysis, which we will try to capture.
            - We have four property groups in this case, which we will merge.
              - GC-TPH
              - GC-TSH
              - GC-TAH
              - Hydrocarbon Content Ratio
            - Dimensional parameters are (weathering).
            - Values Units are split between mg/g and percent.
        '''
        gcts = self.weathering_sliced_obj(('gc_total_petroleum_hydrocarbon',
                                           'gc_total_saturate_hydrocarbon',
                                           'gc_total_aromatic_hydrocarbon'),
                                          suffix='_mg_g',
                                          method='ESTS 2002a')
        gcrs = self.weathering_sliced_obj('hydrocarbon_content_ratio',
                                          suffix='_percent')

        [a.update(b) for a, b in zip(gcts, gcrs)]

        return gcts

    @property
    def ccme(self):
        '''
            The Evironment Canada data sheet contains data for CCME Fractions,
            which we will try to capture.
            We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are all mg/g as far as I can tell.
        '''
        return self.weathering_sliced_obj('ccme_fractions',
                                          suffix='_mg_g',
                                          method='ESTS 2002a')

    @property
    def ccme_f1(self):
        '''
            The Evironment Canada data sheet contains data for CCME Fractions,
            which we will try to capture.  Specifically here, we grab the F1
            Saturate CXX values.
            - We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are not specified.
        '''
        return self.weathering_sliced_obj('saturates_f1',
                                          method='ESTS 2002a')

    @property
    def ccme_f2(self):
        '''
            The Evironment Canada data sheet contains data for CCME Fractions,
            which we will try to capture.  Specifically here, we grab the F2
            Aromatic CXX values.
            - We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are not specified.
        '''
        return self.weathering_sliced_obj('aromatics_f2',
                                          method='ESTS 2002a')

    @property
    def ccme_tph(self):
        '''
            The Evironment Canada data sheet contains data for CCME Fractions,
            which we will try to capture.  Specifically here, we grab the
            GC-TPH (Gas Chromatography - Total Petroleum Hydrocarbons)
            CXX values.
            - We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are not specified.
        '''
        return self.weathering_sliced_obj('gc_tph_f1_plus_f2',
                                          method='ESTS 2002a')

    @property
    def alkylated_pahs(self):
        '''
            The Evironment Canada data sheet contains data for Alkylated Total
            Aromatic Hydrocarbons (PAHs), which we will try to capture.
            - We have seven property groups in this case, which we will merge.
              - Naphthalenes
              - Phenanthrenes
              - Dibenzothiophenes
              - Fluorenes
              - Benzonaphthothiophenes
              - Chrysenes
              - Other Priority PAHs
            - Dimensional parameters are (weathering).
            - Values Units are ug/g
        '''
        return self.weathering_sliced_obj(('naphthalenes',
                                           'phenanthrenes',
                                           'dibenzothiophenes',
                                           'fluorenes',
                                           'benzonaphthothiophenes',
                                           'chrysenes',
                                           'other_priority_pahs'),
                                          suffix='_ug_g',
                                          method='ESTS 2002a')

    @property
    def alkanes(self):
        '''
            The Environment Canada data sheet contains data for n-Alkanes,
            which we will try to capture.
            We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are all ug/g as far as I can tell.
        '''
        return self.weathering_sliced_obj('n_alkanes',
                                          suffix='_ug_g',
                                          method='ESTS 2002a')

    @property
    def biomarkers(self):
        '''
            The Environment Canada data sheet contains data for biomarkers,
            which we will try to capture.
            We have a single property group in this case.
            - Dimensional parameters are (weathering).
            - Values Units are all ug/g as far as I can tell.
        '''
        return self.weathering_sliced_obj('biomarkers',
                                          suffix='_ug_g',
                                          method='ESTS 2002a')

    def weathering_sliced_obj(self, groups, suffix=None, method=None):
        '''
            Generalized method for getting the individual sample-sliced
            attributes from one or more property groups
            :param groups: The group or groups from which to collect the
                           attribute slices.
            :type groups: A string or list of strings.
            :param suffix: Add a suffix to the attribute names.  This is most
                           often used if we are dealing with a homogeneous
                           set of properties with the same units
            :type suffix: A string.
            :param method: Add an attribute for the testing method documented
                           as being used to measure the properties.
            :type method: A string.
        '''
        ret = []
        props = {}

        if isinstance(groups, str):
            groups = [groups]

        [props.update(self.values[c])
         for c in groups]

        for props_i in self.iterate_weathering(props):
            if not all([v is None for k, v in props_i.items()
                        if k is not 'weathering']):
                if suffix is not None:
                    [self._rename_prop(props_i, lbl, lbl + suffix)
                     for lbl in list(props_i.keys())
                     if lbl != 'weathering']

                if method is not None:
                    props_i['method'] = method

                for lbl in list(props_i.keys()):
                    if props_i[lbl] in ('/', ' '):
                        props_i[lbl] = None

                ret.append(props_i)

        return ret

    def _build_kwargs(self, props,
                      add_props=None,
                      prune_props=None,
                      rename_props=None,
                      op_and_value=None):
        '''
            Build a content properties dictionary suitable to be passed in
            as keyword args.
            - props: Our properties from the Excel file.
            - add_props: A set of properties to be added.
            - prune_props: A set of properties to be pruned.
            - rename_props: dict containing properties to be renamed,
            - op_and_value: A set of numeric properties that could contain an
                            operator prefix.

            Note: We perform actions in a particular order.
                  1: Add any add_props that were passed in.
                  2: Prune any prune_props that were passed in.
                  3: Rename any rename_props that were passed in.
                  4: Convert any op_and_value props that may have an operator
                     prefix.  Right now we will just throw away the operator,
                     but in the future we could decide to keep it in its own
                     property.  Depends upon how useful it turns out to be.

            TODO: It is intended that any unit conversions will be handled in
                  an exclusive way.  It is unlikely that we will be performing
                  multiple types of conversions on a single set of kwargs, and
                  it would in fact be wrong to perform multiple conversions
                  on a single attribute.  We should add logic to enforce some
                  exclusivity, at least in this function's current form.
            TODO: It seems that we are handling two distinct things here,
                  management of property names and unit conversion.  We might
                  want to split this into separate functions.
        '''
        kwargs = props.copy()

        if add_props is not None:
            for k, v in add_props.items():
                kwargs[k] = v

        if prune_props is not None:
            for p in prune_props:
                kwargs.pop(p, None)

        if rename_props is not None:
            for old_prop, new_prop in rename_props.items():
                self._rename_prop(kwargs, old_prop, new_prop)

        if op_and_value is not None:
            for ov in op_and_value:
                op, value = self._get_op_and_value(kwargs[ov])

                if op == '<':
                    kwargs[ov] = {'max_value': value, 'min_value': None,
                                  'unit': '1'}
                elif op == '>':
                    kwargs[ov] = {'max_value': None, 'min_value': value,
                                  'unit': '1'}
                else:
                    kwargs[ov] = {'value': value, 'unit': '1'}

        return kwargs

    def build_flash_point_kwargs(self, props):
        '''
            Build a flash point properties dictionary suitable to be passed in
            as keyword args.  This is different enough from the generic
            build_kwargs() that it gets its own function.
            - props: a dictionary of properties
        '''
        fp_kwargs = props

        temp_c = fp_kwargs['flash_point']
        if temp_c is None:
            return None

        del fp_kwargs['flash_point']

        fp_kwargs['ref_temp_c'] = self._get_range_or_scalar(temp_c)
        fp_kwargs['ref_temp_c']['unit'] = 'C'

        return fp_kwargs

    def _build_pour_point_kwargs(self, props):
        '''
            Build a pour point properties dictionary suitable to be passed in
            as keyword args.  This is different enough from the generic
            build_kwargs() that it gets its own function.
            - props: A dictionary of properties
            - weathering: The fractional oil weathering amount.
        '''
        pp_kwargs = props

        temp_c = pp_kwargs['pour_point']
        if temp_c is None:
            return None

        del pp_kwargs['pour_point']

        pp_kwargs['ref_temp_c'] = self._get_range_or_scalar(temp_c)
        pp_kwargs['ref_temp_c']['unit'] = 'C'

        return pp_kwargs

    def _build_evaporation_kwargs(self, props, equation, coeff_label):
        '''
            Build evaporation equation properties dictionary suitable to be
            passed in as keyword args.  This is different enough from the
            generic build_kwargs() that it gets its own function.
            - props: Our properties from the Excel file.
            - weathering: The fractional oil weathering amount.
            - coeff_label: The property label containing our coefficients.
                           This is a suffix that we will prepend with the
                           coefficient we would like to get.
        '''
        evap_kwargs = {}

        evap_kwargs['weathering'] = props['weathering']
        evap_kwargs['equation'] = equation

        evap_kwargs['a'] = props['a_{}'.format(coeff_label)]
        evap_kwargs['b'] = props['b_{}'.format(coeff_label)]

        if 'c_{}'.format(coeff_label) in props:
            evap_kwargs['c'] = props['c_{}'.format(coeff_label)]

        return evap_kwargs

    def _rename_prop(self, kwargs, old_prop, new_prop):
        kwargs[new_prop] = kwargs[old_prop]
        del kwargs[old_prop]

    def _get_range_or_scalar(self, value_in):
        op, value = self._get_op_and_value(value_in)

        if op == '<':
            # range with no min limit
            return {'min_value': None, 'max_value': value}
        elif op == '>':
            # range with no max limit
            return {'min_value': value, 'max_value': None}
        else:
            # scalar value or None.  Either way we return the value
            return {'value': value}

    def _get_op_and_value(self, value_in):
        '''
            Environment Canada sometimes puts a '<' or '>' in front of the
            numeric value in a cell of the Excel spreadsheet.
            In these cases, it is a string indicating greater than or less than
            the float value.  So we need to split the content into an operator
            and a float value.
            Most of the time, it is a float value, in which we just
            interpret it with no associated operator.
        '''
        op = None

        if isinstance(value_in, (int, float)):
            value = value_in
        elif isinstance(value_in, str):
            op = value_in[0]

            if op in ('<', '>'):
                value = value_in[1:].strip()
            else:
                op = None
                value = value_in.strip()

            try:
                value = float(value)
            except ValueError:
                value = None
        else:
            value = None

        return op, value
