#!/usr/bin/env python
from numbers import Number


class MapperBase:
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
        '''
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
