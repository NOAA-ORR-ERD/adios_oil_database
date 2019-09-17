#
# PyMODM Model class definitions for embedded content in our oil records
#
from itertools import zip_longest

from unit_conversion import convert
from unit_conversion.unit_data import ConvertDataUnits

from pymodm.base.models import MongoModelMetaclass
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class UnitMeta(MongoModelMetaclass):
    def __new__(cls, name, bases, namespace):
        # we will only try this if we are a 'Unit' type class
        max_length = 32

        namespace['unit_type'] = None

        if name.endswith('Unit'):
            unit_type = cls.camelcase_to_space(name[:-4])
            try:
                all_units = [[k] + v[1]
                             for k, v
                             in ConvertDataUnits[unit_type].items()]
                flattened_units = tuple(set([i for sub in all_units
                                             for i in sub]))

                namespace['unit'] = CharField(max_length=max_length,
                                              choices=flattened_units)
                namespace['unit_type'] = unit_type
            except KeyError:
                namespace['unit'] = CharField(max_length=max_length)
        else:
            namespace['unit'] = CharField(max_length=max_length)

        return super(UnitMeta, cls).__new__(cls, name, bases, namespace)

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


class FloatUnit(EmbeddedMongoModel, metaclass=UnitMeta):
    '''
        Primitive structure for representing floating point values in
        a defined unit.  This will be used for most oil property values,

        Note: In the future, we may want to subclass this to restrict the
              unit descriptions to a set that makes sense for the particular
              oil property we are concerned with.  For example, a FloatUnit
              describing density would be restricted to only unit values
              {'kg/m^3', 'g/cm^3'}
              Of course, this would add extra fields
    '''
    value = FloatField(blank=True)
    min_value = FloatField(blank=True)
    max_value = FloatField(blank=True)

    def __init__(self, **kwargs):
        '''
            Input args with defaults:

            :param value: A numeric value
            :param unit: A representation of units that the value is to
                         describe.
            :param from_unit=None: The unit representation of the incoming
                                   value if the value is to be converted
                                   before storage in the class
        '''
        if hasattr(kwargs['unit'], 'decode'):
            # ensure we are working with a unicode unit value
            kwargs['unit'] = kwargs['unit'].decode('utf-8')

        if 'from_unit' in kwargs and kwargs['from_unit'] is not None:
            self._convert_value_arg(kwargs)

        for k in list(kwargs.keys()):
            if (k not in self.__class__.__dict__):
                del kwargs[k]

        super(FloatUnit, self).__init__(**kwargs)

    def _convert_value_arg(self, kwargs):
        from_unit, unit = kwargs['from_unit'], kwargs['unit']

        if hasattr(from_unit, 'decode'):
            # ensure we are working with a unicode from_unit value
            from_unit = from_unit.decode('utf-8')

        value, min_value, max_value = [kwargs.get(a, None)
                                       for a in ('value',
                                                 'min_value',
                                                 'max_value')]

        if not (from_unit in self.__class__.unit.choices and
                unit in self.__class__.unit.choices):
            raise ValueError('Invalid conversion from {} to {}'
                             .format(from_unit, unit))

        for a, v in zip(('value', 'min_value', 'max_value'),
                        (value, min_value, max_value)):
            if v is not None:
                kwargs[a] = convert(self.unit_type, from_unit, unit, v)

    def to_unit(self, new_unit):
        if new_unit not in self.__class__.unit.choices:
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
