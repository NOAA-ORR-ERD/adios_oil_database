#!/usr/bin/env python
import logging
import re

from ..parser import ParserBase

logger = logging.getLogger(__name__)


class OilLibraryRecordParser(ParserBase):
    '''
        A record parsing class for the NOAA Oil Library spreadsheet.
        - We manage a list of properties extracted from an Excel row for an
          oil.
        - The raw data from the Excel file will be a flat list, even for
          multidimensional properties like densities, viscosities, and
          distillation cuts.
    '''
    def __init__(self, values, file_props):
        '''
            :param values: A dict of property names/values.

            Basically, we will do some light massaging of the names and values
            of our incoming properties, and then we will directly apply them
            to our __dict__.
        '''
        self.__dict__.update(self._privatize_data_properties(
            self._slugify_keys(values)
        ))
        self.file_props = file_props

    def _slugify_keys(self, obj):
        '''
            Generate a structure like the incoming data, but with keys that
            have been 'slugified', which is to say turned into a string that
            is suitable for use as an object attribute.
        '''
        if isinstance(obj, (tuple, list, set, frozenset)):
            return [self._slugify_keys(v) for v in obj]
        elif isinstance(obj, dict):
            return dict([(self.slugify(k), self._slugify_keys(v))
                        for k, v in obj.items()])
        else:
            return obj

    def _privatize_data_properties(self, obj):
        '''
            Certain named data properties need to be handled as special cases
            by the parser.  This will be handled with a property definition
            that sometimes has the same name as the original data property.

            So to ensure the original property doesn't get clobbered, we need
            to turn them into private members (add an underscore to the name).
        '''
        for name in ('reference',
                     'synonyms',
                     'pour_point_min_k', 'pour_point_max_k',
                     'flash_point_min_k', 'flash_point_max_k',
                     'preferred_oils', 'product_type',
                     'cut_units', 'oil_class'):
            self._privatize_data_property(obj, name)

        return obj

    def _privatize_data_property(self, kwargs, name):
        kwargs[f'_{name}'] = kwargs.pop(name)

    @property
    def source_id(self):
        return self.adios_oil_id

    @property
    def oil_id(self):
        return self.adios_oil_id

    @property
    def _id(self):
        return self.adios_oil_id

    @property
    def name(self):
        return self.oil_name

    @property
    def API(self):
        return self.api

    @property
    def sulfur(self):
        return self.sulphur

    @property
    def reference(self):
        '''
            The reference content can have:
            - no content:  In this case we take the created date of the
                           .csv file header.
            - one year (YYYY):  In this case we parse the year as an int and
                                form a datetime with it.
            - multiple years (YYYY): In this case we use the highest numeric
                                     year (most recent) and form a datetime
                                     with it.
        '''
        ref_text = self._reference

        if ref_text is None:
            occurrences = []
        else:
            occurrences = [int(n)
                           for n in re.compile(r'\d{4}').findall(ref_text)]

        if len(occurrences) == 0:
            ref_year = self.file_props['created'].year
        else:
            ref_year = max(occurrences)

        return {'reference': ref_text, 'year': ref_year}

    @property
    def synonyms(self):
        '''
            Synonyms is a single string field that contains a comma separated
            list of substring names
        '''
        if self._synonyms is None or self._synonyms.strip() == '':
            return None
        else:
            return [{'name': s.strip()}
                    for s in self._synonyms.split(',')
                    if len(s) > 0]

    @property
    def pour_point_min_k(self):
        min_k, max_k = self._pour_point_min_k, self._pour_point_max_k

        if min_k == '<':
            min_k = None
        elif min_k == '>':
            min_k = max_k

        return min_k

    @property
    def pour_point_max_k(self):
        min_k, max_k = self._pour_point_min_k, self._pour_point_max_k

        if min_k == '>':
            max_k = None

        return max_k

    @property
    def flash_point_min_k(self):
        min_k, max_k = self._flash_point_min_k, self._flash_point_max_k

        if min_k == '<':
            min_k = None
        elif min_k == '>':
            min_k = max_k

        return min_k

    @property
    def flash_point_max_k(self):
        min_k, max_k = self._flash_point_min_k, self._flash_point_max_k

        if min_k == '>':
            max_k = None

        return max_k

    @property
    def preferred_oils(self):
        return True if self._preferred_oils == 'X' else False

    @property
    def product_type(self):
        if self._product_type is not None:
            return self._product_type.lower()
        else:
            return None

    @property
    def cut_units(self):
        if self._cut_units is not None:
            return self._cut_units.lower()
        else:
            return None

    @property
    def oil_class(self):
        if self._oil_class is not None:
            return self._oil_class.lower()
        else:
            return None

    def get_property_sets(self, num_sets, obj_name, obj_argnames,
                          required_obj_args):
        '''
            Generalized method of getting lists of data sets out of our record.

            Since our data source is a single fixed row of data, there will be
            a number of fixed subsets of object data attributes, but they may
            or may not be filled with data.
            For these property sets, the column names are organized with the
            following naming convention:
                '<attr><instance>_<sub_attr>'

            Where:
                <attr>     = The name of the attribute list.
                <instance> = An index in the range [1...N+1] where N is the
                             number of instances in the list.
                <sub_attr> = The name of an attribute contained within an
                             instance of the list.

            Basically we will return a set of object properties for each
            instance that contains a defined set of required argument
            attributes.
        '''
        ret = []

        for i in range(1, num_sets + 1):
            obj_kwargs = {}

            parser_attrs = ['{}{}_{}'.format(obj_name, i, a)
                            for a in obj_argnames]

            for attr, obj_arg in zip(parser_attrs, obj_argnames):
                if hasattr(self, attr):
                    value = getattr(self, attr)

                    if value is not None and value != '':
                        obj_kwargs[obj_arg] = value

            if all([i in obj_kwargs for i in required_obj_args]):
                ret.append(obj_kwargs)

        return ret

    @property
    def pour_point(self):
        ret = {'unit': 'K'}

        min_value = self.pour_point_min_k
        max_value = self.pour_point_max_k

        if min_value is None and max_value is None:
            ret = None
        elif min_value == max_value:
            ret['value'] = min_value
        else:
            ret['min_value'] = min_value
            ret['max_value'] = max_value

        return ret

    @property
    def flash_point(self):
        ret = {'unit': 'K'}

        min_value = self.flash_point_min_k
        max_value = self.flash_point_max_k

        if min_value is None and max_value is None:
            ret = None
        elif min_value == max_value:
            ret['value'] = min_value
        else:
            ret['min_value'] = min_value
            ret['max_value'] = max_value

        return ret

    @property
    def densities(self):
        ret = []
        dens = self.get_property_sets(4, 'density',
                                      ('kg_m_3', 'ref_temp_k', 'weathering'),
                                      ('kg_m_3', 'ref_temp_k'))

        for d in dens:
            ret.append({
                'density': {'value': d['kg_m_3'], 'unit': 'kg/m^3'},
                'ref_temp': {'value': d['ref_temp_k'], 'unit': 'K'},
                'weathering': d.get('weathering', 0.0),
            })

        return ret

    @property
    def kinematic_viscosities(self):
        ret = []
        visc = self.get_property_sets(6, 'kvis',
                                      ('m_2_s', 'ref_temp_k', 'weathering'),
                                      ('m_2_s', 'ref_temp_k'))

        for v in visc:
            ret.append({
                'viscosity': {'value': v['m_2_s'], 'unit': 'm^2/s'},
                'ref_temp': {'value': v['ref_temp_k'], 'unit': 'K'},
                'weathering': v.get('weathering', 0.0),
            })

        return ret

    @property
    def dynamic_viscosities(self):
        ret = []
        visc = self.get_property_sets(6, 'dvis',
                                      ('kg_ms', 'ref_temp_k', 'weathering'),
                                      ('kg_ms', 'ref_temp_k'))
        for v in visc:
            ret.append({
                'viscosity': {'value': v['kg_ms'], 'unit': 'kg/(m s)'},
                'ref_temp': {'value': v['ref_temp_k'], 'unit': 'K'},
                'weathering': v.get('weathering', 0.0),
            })

        return ret

    @property
    def cuts(self):
        ret = []
        cuts = self.get_property_sets(15, 'cut',
                                      ('vapor_temp_k', 'liquid_temp_k',
                                       'fraction'),
                                      ('vapor_temp_k', 'fraction'))

        if self.cut_units in ('volume', 'Volume'):
            unit_type = 'volumefraction'
        else:
            unit_type = 'massfraction'

        for c in cuts:
            value = {
                'fraction': {'value': c['fraction'],
                             'unit': '1',
                             'unit_type': unit_type},
                'vapor_temp': {'value': c['vapor_temp_k'], 'unit': 'K'},
            }

            if c.get('liquid_temp_k', None) is not None:
                value['liquid_temp'] = {'value': c['liquid_temp_k'],
                                        'unit': 'K'}

            ret.append(value)

        return ret

    @property
    def toxicities(self):
        effective = self.get_property_sets(3, 'tox_ec',
                                           ('species', '24h', '48h', '96h'),
                                           ('species',))

        lethal = self.get_property_sets(3, 'tox_lc',
                                        ('species', '24h', '48h', '96h'),
                                        ('species',))

        [(e.update({'tox_type': 'EC'})) for e in effective]
        [(l.update({'tox_type': 'LC'})) for l in lethal]

        all_tox = effective + lethal

        for t in all_tox:
            for d in ('24h', '48h', '96h'):
                if d in t:
                    t['after_{}'.format(d)] = float(t[d])
                    t.pop(d, None)

        return all_tox

    @property
    def interfacial_tensions(self):
        ret = []

        for intf in ('water', 'seawater'):
            value = getattr(self, f'oil_{intf}_interfacial_tension_n_m')
            temp = getattr(self, f'oil_{intf}_interfacial_tension_ref_temp_k')

            if value is not None:
                ret.append({
                    'interface': intf,
                    'method': None,
                    'tension': {'value': value, 'unit': 'N/m'},
                    'ref_temp': {'value': temp, 'unit': 'K'}
                })

        return ret

    @property
    def emulsions(self):
        '''
            Oil Library records have some attributes related to emulsions:
            - emuls_constant_min: Zero percent emulsion weathered amount
            - emuls_constant_max: Max percent emulsion weathered amount
            - water_content_emulsion: water content at max weathered

            - Age will be set to the day of formation
            - Temperature will be set to 15C (288.15K)
        '''
        ret = []

        water = self.water_content_emulsion

        if water is not None:
            emuls_min = self.emuls_constant_min
            emuls_max = self.emuls_constant_max

            if emuls_min is None and emuls_max is None:
                # apply water to the fresh sample
                ret.append({
                    'water_content': {'value': water, 'unit': '1'},
                    'age': {'value': 0.0, 'unit': 'day'},
                    'ref_temp': {'value': 288.15, 'unit': 'K'},
                    'weathering': 0.0,
                })
            else:
                if emuls_min not in (None, 0.0):
                    # we have a min weathering sample
                    ret.append({
                        'water_content': {'value': 0.0, 'unit': '1'},
                        'age': {'value': 0.0, 'unit': 'day'},
                        'ref_temp': {'value': 288.15, 'unit': 'K'},
                        'weathering': emuls_min,
                    })

                if emuls_max is not None:
                    # we have a max weathering sample
                    ret.append({
                        'water_content': {'value': water, 'unit': '1'},
                        'age': {'value': 0.0, 'unit': 'day'},
                        'ref_temp': {'value': 288.15, 'unit': 'K'},
                        'weathering': emuls_max,
                    })

        return ret

    @property
    def conradson(self):
        ret = {}

        residue = self.conrandson_residuum
        crude = self.conrandson_crude

        if residue is not None:
            ret['residue'] = {'value': residue, 'unit': '1'}

        if crude is not None:
            ret['crude'] = {'value': crude, 'unit': '1'}

        if len(ret) == 0:
            ret = None

        return ret

    @property
    def SARA(self):
        ret = {}

        for sara_type in ('saturates', 'aromatics', 'resins', 'asphaltenes'):
            fraction = getattr(self, sara_type)

            if fraction is not None:
                ret[sara_type] = {'value': fraction, 'unit': '1'}

        if len(ret) == 0:
            ret = None

        return ret

    @property
    def weathering(self):
        '''
            A NOAA Filemaker record is a flat row of data, but there are some
            attributes that have weathering associated with their measured
            values.  These attributes are:
            - Density
            - KVis
            - Dvis

            In addition to these weathered attributes, the emulsion constant
            attributes are applied in the context of weathered samples.
            - The min emulsification constant is Emuls_Constant_Min.  Its value
              is a weathered amount.
            - The max emulsification constant is Emuls_Constant_Max.  Its value
              is a weathered amount.

            All other attributes should be implicitly regarded as fresh oil
            measurements.
        '''
        weathered_amounts = set((0.0,))

        for k, v in self.__dict__.items():
            if k.endswith('weathering') and k != 'weathering':
                v = 0.0 if v is None else v
                weathered_amounts.add(v)

        for attr in ('emuls_constant_min', 'emuls_constant_max'):
            v = getattr(self, attr)
            v = 0.0 if v is None else v
            weathered_amounts.add(v)

        return sorted(list(weathered_amounts))
