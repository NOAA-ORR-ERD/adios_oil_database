#!/usr/bin/env python
import re
from functools import wraps
from collections import defaultdict
from datetime import datetime
from pytz import timezone
import logging

from slugify import Slugify

custom_slugify = Slugify(to_lower=True, separator='_')

logger = logging.getLogger(__name__)


# Here we map some of the more unwieldy labels to simpler ones
# These labels could appear at any level of the hierarchy
label_map = {
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
    'ests_emergencies_sciences_and_technologies_code': 'ests_code',
    'evaporation_ests_1998_1': 'evaporation',
    'parameters_for_evaporation_equation_mass_loss': 'evaporation_mass_loss',
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
        ret = func(*args, **kwargs)
        if isinstance(ret, (tuple, list, set, frozenset)):
            return [parse_single_datetime(dt) for dt in ret]
        else:
            return parse_single_datetime(ret)

    return wrapper


class ParserBase(object):
    def slugify(self, label):
        '''
            Generate a string that is suitable for use as an object attribute.
            - The strings will be snake-case, all lowercase words separated
              by underscores.
            - They will not start with a numeric digit.  If the original label
              starts with a digit, the slug will be prepended with an
              underscore ('_').

            Note: Some unicode characters are not intuitive.  Specifically,
                  In German orthography, the grapheme ß, called Eszett or
                  scharfes S (Sharp S).  It looks sorta like a capital B to
                  English readers, but converting it to 'ss' is not completely
                  inappropriate.
        '''
        if label is None:
            return label

        prefix = '_' if label[0].isdigit() else ''

        return prefix + custom_slugify(label)


class EnvCanadaRecordParser(ParserBase):
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
            :param values: A dictionary of property values.
            :type values: A dictionary structure with raw property names
                          as keys, and associated values.
            :param file_props: A dictionary of property values concerning the
                               source xl spreadsheet.
            :type file_props: A dictionary structure with property names
                              as keys, and associated values.
        '''
        self.values = self._slugify_keys(values)
        self.labels = self._generate_labels(values)
        self._propagate_merged_cells()
        self.file_props = file_props

    def _slugify_keys(self, obj):
        '''
            Generate a structure like the incoming data, but with keys that
            have been 'slugified', which is to say turned into a string that
            is suitable for use as an object attribute.
        '''

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

    def get_label(self, nav_list):
        '''
            For an attribute in our values hierarchy, get the original source
            label information.

            Ex:
                parser_obj.get_label(('gc_total_aromatic_hydrocarbon.tah'))
        '''
        if isinstance(nav_list, str):
            nav_list = nav_list.split('.')

        labels = {'value': self.labels}

        for l in nav_list:
            labels = labels['value'][l]

        return labels['label']

    def _propagate_merged_cells(self):
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
    def reference(self):
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
        ref_text = ' '.join([f for f in self.values[None]['reference']
                            if f is not None])

        occurrences = [int(n) for n in re.compile(r'\d{4}').findall(ref_text)]

        if len(occurrences) == 0:
            ref_year = self.file_props['created'].year
        else:
            ref_year = max(occurrences)

        return {'reference': ref_text, 'year': ref_year}

    @property
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
            return 'refined'
        else:
            return 'crude'

    def _product_type_is_probably_refined(self):
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

    def vertical_slice(self, index):
        '''
            All values in our self.values structure will be a list that
            conforms to the weathering subsamples for a record
            Recursively navigate values structure
        '''
        return dict([(cat_key,
                      dict([(k, v[index]) for k, v in cat_val.items()]))
                     for cat_key, cat_val in self.values.items()])

    @property
    def sub_samples(self):
        for i, w in enumerate(self.weathering):
            props_i = self.vertical_slice(i)
            props_i['weathering'] = w

            yield EnvCanadaSampleParser(props_i)

    def dict(self):
        ret = {}

        for attr in ('name',
                     'oil_id',
                     'location',
                     'reference',
                     'sample_date',
                     'comments',
                     'product_type'):
            ret[attr] = getattr(self, attr)

        ret['samples'] = list(self.sub_samples)

        return ret


class EnvCanadaSampleParser(ParserBase):
    '''
        A sample class for the Environment Canada oil spreadsheet.  This is
        intended to be used with a set of data representing a single subsample
        inside an oil record.
        - We manage a hierarcical structure of properties similar to that of
          the record parser
        - The data associated with any individual property will be a single
          scalar value corresponding to a weathered subsample that exists
          for an oil record.
    '''
    attr_map = {
        # any attributes that are a simple mapping of the data
        'adhesion': 'adhesion',
        'flash_point': 'flash_point_c',
        'pour_point': 'pour_point_c',
        'boiling_point_distribution': ('boiling_point_distribution_'
                                       'temperature_c'),
        'boiling_point_cumulative_fraction': ('boiling_point_'
                                              'cumulative_weight_fraction'),
        'chemical_dispersibility': 'chemical_dispersibility_with_corexit_9500',
        'sulfur_content': 'sulfur_content',
        'water_content': 'water_content',
        'wax_content': 'wax_content',
        'sara_total_fractions': 'hydrocarbon_group_content',
        'benzene': 'benzene_and_alkynated_benzene',
        'btex_group': 'btex_group',
        'c4_c6_alkyl_benzenes': 'c4_c6_alkyl_benzenes',
        'headspace_analysis': 'headspace_analysis',
        'ccme': 'ccme_fractions',
        'ccme_f1': 'saturates_f1',
        'ccme_f2': 'aromatics_f2',
        'ccme_tph': 'gc_tph_f1_plus_f2',
        'naphthalenes': 'naphthalenes',
        'phenanthrenes': 'phenanthrenes',
        'dibenzothiophenes': 'dibenzothiophenes',
        'fluorenes': 'fluorenes',
        'benzonaphthothiophenes': 'benzonaphthothiophenes',
        'chrysenes': 'chrysenes',
        'other_priority_pahs': 'other_priority_pahs',
        'n_alkanes': 'n_alkanes',
        'biomarkers': 'biomarkers',
    }

    def __init__(self, values):
        '''
            :param values: A dictionary of property values.
            :type values: A dictionary structure with raw property names
                          as keys, and associated values.
        '''
        self.values = values

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

        for p in props:
            yield p, getattr(self, p)

    def dict(self):
        attrs = set(self.attr_map.keys())

        [attrs.add(p) for p in dir(self.__class__)
         if isinstance(getattr(self.__class__, p), property)]

        return dict([(a, getattr(self, a)) for a in attrs])

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
        try:
            ret = self.values.get(self.attr_map[name])
        except Exception:
            logger.info('EnvCanadaSampleParser.{} not found'.format(name))
            raise

        return ret

    @property
    def api(self):
        return self.deep_get('api_gravity.gravity')

    @property
    def densities(self):
        '''
            There are two categories, density at 15C, and density at 0/5C.
        '''
        ret = defaultdict(list)

        items = (list(self.values['density_at_15_c'].items()) +
                 list(self.values['density_at_0_5_c'].items()))

        for k, v in items:
            if k in ('standard_deviation', 'replicates'):
                ret[k].append(v)
            else:
                ret[k] = v

        return ret

    @property
    def dvis(self):
        '''
            There are two categories, viscosity at 15C, and viscosity at 0/5C.

            Note: Sometimes there is a greater than ('>') indication for a
                  viscosity value.  In this case, we parse the float value
                  as an interval with the operator indicating whether it is
                  a min or a max.
        '''
        ret = defaultdict(list)

        items = (list(self.values['viscosity_at_15_c'].items()) +
                 list(self.values['viscosity_at_0_5_c'].items()))

        for k, v in items:
            if k in ('standard_deviation', 'replicates'):
                ret[k].append(v)
            else:
                ret[k] = v

        return ret

    @property
    def ift(self):
        '''
            Getting interfacial tensions out of this datasheet is a bit tricky,
            but understandably so since we are dealing with a number of
            dimensional parameters (temperature, interface, weathering).
            There are two categories, surface/interfacial tension at 15C, and
            surface/interfacial tension at 0/5C.
        '''
        ret = defaultdict(list)

        items = (list(self.values['ift_at_15_c'].items()) +
                 list(self.values['ift_at_0_5_c'].items()))

        for k, v in items:
            if k in ('standard_deviation', 'replicates', 'method'):
                ret[k].append(v)
            else:
                ret[k] = v

        for k in ('standard_deviation', 'replicates'):
            # flatten the list
            ret[k] = [i for sub in ret[k] for i in sub]

        return ret

    @property
    def evaporation_eqs(self):
        ret = defaultdict(list)

        items = (list(self.values['evaporation'].items()) +
                 list(self.values['evaporation_mass_loss'].items()))

        ret.update(items)

        return ret

    @property
    def emulsion(self):
        for category in ('emulsion_at_15_c_day_0', 'emulsion_at_15_c_day_7'):
            yield self.values[category]

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
        return dict(
            list(self.values['gc_total_petroleum_hydrocarbon'].items()) +
            list(self.values['gc_total_saturate_hydrocarbon'].items()) +
            list(self.values['gc_total_aromatic_hydrocarbon'].items()) +
            list(self.values['hydrocarbon_content_ratio'].items())
        )
