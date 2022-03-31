#!/usr/bin/env python
from numbers import Number

from .importer_base import custom_slugify, ImporterBase


class MapperBase(ImporterBase):
    def measurement(self, value, unit, unit_type=None,
                    standard_deviation=None, replicates=None):
        mm_value = self.min_max(value)

        if mm_value[0] == mm_value[1]:
            ret = {'value': value, 'unit': unit}
        else:
            ret = {'min_value': mm_value[0],
                   'max_value': mm_value[1],
                   'unit': unit}

        if unit_type is not None:
            ret['unit_type'] = unit_type

        if standard_deviation is not None:
            ret['standard_deviation'] = standard_deviation

        if replicates is not None:
            ret['replicates'] = replicates

        return ret

    def compound(self, name, measurement, method=None, groups=None,
                 sparse=False):
        """
        Example of content::

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
        """
        ret = {'name': name, 'measurement': measurement}

        if method is not None or sparse is False:
            ret['method'] = method

        if groups is not None or sparse is False:
            ret['groups'] = groups

        return ret

    def min_max(self, value):
        if value is None or isinstance(value, Number):
            return [value, value]

        try:
            op, num = value[0], float(value[1:])
        except ValueError:
            return [None, None]  # could not convert to number

        if op == '<':
            return [None, num]
        elif op == '>':
            return [num, None]
        else:
            return [None, None]  # can't determine a range

    @classmethod
    def slugify(cls, label):
        """
        Generate a string that is suitable for use as an object attribute.

        - The strings will be snake-case, all lowercase words separated
          by underscores.

        - They will not start with a numeric digit.  If the original label
          starts with a digit, the slug will be prepended with an
          underscore ('_').

        **Note:** Some unicode characters are not intuitive.  Specifically,
        In German orthography, the grapheme ß, called Eszett or
        scharfes S (Sharp S).  It looks sorta like a capital B to
        English readers, but converting it to 'ss' is not completely
        inappropriate.

        **Note:** this function is duplicated in the mapper.  Perhaps a base
        class to all the importer types.
        """
        if label is None:
            return label

        prefix = '_' if label[0].isdigit() else ''

        return prefix + custom_slugify(label)
