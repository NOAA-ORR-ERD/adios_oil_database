#
# Model class definitions for embedded Float/Unit content pairs
# in our oil records
#
from pydantic.dataclasses import dataclass
from itertools import zip_longest

from unit_conversion import convert
from unit_conversion.unit_data import ConvertDataUnits


class UnitMeta(type):
    def __new__(cls, name, bases, namespace):
        # we will only try this if we are a 'Unit' type class
        #
        # Special Case: the FloatUnit class doesn't have an associated unit
        #               type stanza in PyNUCOS, so we load it with a few
        #               generic fractional unit types.
        if name.endswith('Unit'):
            unit_type = cls.camelcase_to_space(name[:-4])

            try:
                all_units = [[k] + v[1]
                             for k, v
                             in ConvertDataUnits[unit_type].items()]
                flattened_units = tuple(set([i for sub in all_units
                                             for i in sub]))
            except KeyError:
                flattened_units = ['1', '%']

            namespace['unit_choices'] = flattened_units
            namespace['unit_type'] = unit_type
        else:
            namespace['unit_choices'] = ['1', '%']
            namespace['unit_type'] = 'Float'

        return super().__new__(cls, name, bases, namespace)

    @classmethod
    def camelcase_to_space(cls, camelcase, lower=False):
        return cls.camelcase_to_sep(camelcase, lower=lower)

    @classmethod
    def camelcase_to_underscore(cls, camelcase, lower=False):
        return cls.camelcase_to_sep(camelcase, sep='_', lower=lower)

    @classmethod
    def camelcase_to_sep(cls, camelcase, sep=' ', lower=False):
        ret = sep.join(cls.separate_camelcase(camelcase))

        if lower:
            return ret.lower()
        else:
            return ret

    @classmethod
    def separate_camelcase(cls, camelcase):
        idxs = [i for i, c in enumerate(camelcase) if c.isupper()]

        return [camelcase[begin:end]
                for (begin, end) in zip_longest(idxs, idxs[1:])]


@dataclass
class FloatUnit(object, metaclass=UnitMeta):
    '''
        Primitive structure for representing floating point values in
        a defined unit.  This will be used for most oil property values,

        In order to perform unit conversions, subclasses of this need to
        restrict the allowed units to a set that makes sense for the particular
        oil property we are concerned with.
        For example, a FloatUnit describing density would be restricted
        to only unit values
              {'kg/m^3', 'g/cm^3', ...}

        For this, we make use of a metaclass that adds some extra fields
        based on a unit type contained in the subclasses name.  For example,
        a subclass named DensityUnit will grab all the possible density units
        from the unit data table inside the PyNUCOS package.
    '''
    unit: str
    from_unit: str = None

    value: float = None
    min_value: float = None
    max_value: float = None

    def __post_init__(self):
        if hasattr(self.unit, 'decode'):
            self.unit = self.unit.decode('utf-8')

        if self.unit not in self.__class__.unit_choices:
            raise ValueError('{}: Invalid unit passed in {}'
                             .format(self.__class__.__name__, repr(self.unit)))

        if self.from_unit is not None:
            self._convert_value_arg()

    def _convert_value_arg(self):
        if hasattr(self.from_unit, 'decode'):
            # ensure we are working with a unicode from_unit value
            self.from_unit = self.from_unit.decode('utf-8')

        if not (self.from_unit in self.__class__.unit_choices and
                self.unit in self.__class__.unit_choices):
            raise ValueError('Invalid conversion from {} to {}'
                             .format(self.from_unit, self.unit))

        for a, v in zip(('value', 'min_value', 'max_value'),
                        (self.value, self.min_value, self.max_value)):
            if v is not None:
                setattr(self, a,
                        convert(self.unit_type, self.from_unit, self.unit, v))

    def to_unit(self, new_unit):
        if new_unit not in self.__class__.unit_choices:
            raise ValueError('Invalid conversion from {} to {}'
                             .format(self.unit, new_unit))

        if self.value is not None:
            return convert(self.unit_type, self.unit, new_unit, self.value)
        elif any([v is not None for v in (self.min_value, self.max_value)]):
            return [convert(self.unit_type, self.unit, new_unit, v)
                    for v in (self.min_value, self.max_value)]
        else:
            raise RuntimeError('Object has no valid values to convert')

    def __str_unit__(self):
        if self.unit == '1':
            return ''
        else:
            return ' {}'.format(self.unit)

    def __str_scalar__(self):
        return '{}{}'.format(self.value, self.__str_unit__())

    def __str_interval__(self):
        if self.min_value is not None and self.min_value == self.max_value:
            return '{}{}'.format(self.min_value, self.__str_unit__())
        if all([v is not None for v in (self.min_value, self.max_value)]):
            return '[{}\u2192{}]{}'.format(self.min_value, self.max_value,
                                           self.__str_unit__())
        elif self.min_value is not None:
            return '>{}{}'.format(self.min_value, self.__str_unit__())
        elif self.max_value is not None:
            return '<{}{}'.format(self.max_value, self.__str_unit__())
        else:
            return ''

    def __str__(self):
        if self.value is not None:
            return self.__str_scalar__()
        elif any([v is not None for v in (self.min_value, self.max_value)]):
            return self.__str_interval__()
        else:
            return ''

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.__str__())

    def to_json(self):
        ret = {'_cls': '{}.{}'.format(self.__class__.__module__,
                                      self.__class__.__name__)}
        for k in self.__dataclass_fields__.keys():
            value = getattr(self, k)
            if value is not None:
                ret[k] = value

        return ret


class AdhesionUnit(FloatUnit):
    pass


class AngularMeasureUnit(FloatUnit):
    pass


class AreaUnit(FloatUnit):
    pass


class ConcentrationInWaterUnit(FloatUnit):
    pass


class DensityUnit(FloatUnit):
    pass


class DischargeUnit(FloatUnit):
    pass


class DynamicViscosityUnit(FloatUnit):
    pass


class InterfacialTensionUnit(FloatUnit):
    pass


class KinematicViscosityUnit(FloatUnit):
    pass


class LengthUnit(FloatUnit):
    pass


class MassUnit(FloatUnit):
    pass


class OilConcentrationUnit(FloatUnit):
    pass


class TemperatureUnit(FloatUnit):
    pass


class TimeUnit(FloatUnit):
    pass


class VelocityUnit(FloatUnit):
    pass


class VolumeUnit(FloatUnit):
    pass
