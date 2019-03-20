#!/usr/bin/env python
import logging
import re
from itertools import izip_longest

from slugify import slugify_filename

logger = logging.getLogger(__name__)


class OilLibraryRecordParser(object):
    '''
        A record class for the NOAA Oil Library spreadsheet.
        - We manage a list of properties extracted from an Excel row for an
          oil.
        - The raw data from the Excel file will be a flat list, even for
          multidimensional properties like densities, viscosities, and
          distillation cuts.
    '''
    def __init__(self, property_names, values):
        '''
            :param property_names: A list of property names.

            :param values: A list of property values.

            Basically, we will do some light massaging of the names and values
            of our incoming properties, and then we will directly apply them
            to our __dict__.
            Additional customized properties will be defined for anything
            that requires special treatment.
        '''
        file_columns = [slugify_filename(c).lower()
                        for c in property_names]
        values = [v.strip() if v is not None else None
                  for v in values]
        row_dict = dict(izip_longest(file_columns, values))

        self._privatize_data_properties(row_dict)

        self.__dict__.update(row_dict)

    def _privatize_data_properties(self, kwargs):
        '''
            Certain named data properties need to be handled as special cases
            by the parser.  So in order to do this, we need to turn them into
            private members.
            This will allow us to create special case properties that have the
            original property name.
        '''
        for name in ('synonyms',
                     'pour_point_min_k', 'pour_point_max_k',
                     'flash_point_min_k', 'flash_point_max_k',
                     'preferred_oils', 'product_type',
                     'cut_units', 'oil_class'):
            self._privatize_data_property(kwargs, name)
        pass

    def _privatize_data_property(self, kwargs, name):
        '''
            Prepend a named keyward argument with an underscore,
            making it a 'private' property.
        '''
        new_name = '_{}'.format(name)

        kwargs[new_name] = kwargs[name]
        del kwargs[name]

    def get_interface_properties(self):
        '''
            These are all the property names that define the data in an
            Oil Library record.  They include the raw data column names
            plus any date items that needed to be redefined as special cases.
        '''
        props = set([k for k in self.__dict__
                     if not k.startswith('_')])
        props = props.union(set([p for p in dir(self.__class__)
                                 if isinstance(getattr(self.__class__, p),
                                               property)]))
        return props

    @property
    def oil_id(self):
        return self.adios_oil_id

    @property
    def reference_date(self):
        '''
            There is no defined reference date in an Oil Library record.
            There is however the possibility that a year of publication is
            contained within the reference text.
            We will try to find a year value within the reference field
            and return it.  Otherwise we return None
        '''
        if self.reference is None:
            return None
        else:
            expression = re.compile(r'\d{4}')
            occurences = expression.findall(self.reference)

            if len(occurences) == 0:
                return None
            else:
                # just return the first one
                return occurences[0]

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
    def densities(self):
        return self.get_property_sets(4, 'density',
                                      ('kg_m_3', 'ref_temp_k', 'weathering'),
                                      ('kg_m_3', 'ref_temp_k'))

    @property
    def kvis(self):
        return self.get_property_sets(6, 'kvis',
                                      ('m_2_s', 'ref_temp_k', 'weathering'),
                                      ('m_2_s', 'ref_temp_k'))

    @property
    def dvis(self):
        return self.get_property_sets(6, 'dvis',
                                      ('kg_ms', 'ref_temp_k', 'weathering'),
                                      ('kg_ms', 'ref_temp_k'))

    @property
    def cuts(self):
        return self.get_property_sets(15, 'cut',
                                      ('vapor_temp_k', 'liquid_temp_k',
                                       'fraction'),
                                      ('vapor_temp_k', 'fraction'))

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
                    t['after_{}'.format(d)] = t[d]

        return all_tox
