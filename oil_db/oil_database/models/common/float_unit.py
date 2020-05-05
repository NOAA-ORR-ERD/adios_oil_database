#
# Model class definitions for embedded Float/Unit content pairs
# in our oil records
#
import json
from pydantic.dataclasses import dataclass

from unit_conversion import convert
from unit_conversion.unit_data import ConvertDataUnits

from oil_database.util.decamelize import camelcase_to_space


class UnitMeta(type):
    def __new__(cls, name, bases, namespace):
        # we will only try this if we are a 'Unit' type class
        #
        # Special Case: the FloatUnit class doesn't have an associated unit
        #               type stanza in PyNUCOS, so we load it with a few
        #               generic fractional unit types.
        if name.endswith('Unit'):
            unit_type = camelcase_to_space(name[:-4])

            try:
                all_units = [[k] + v[1]
                             for k, v
                             in ConvertDataUnits[unit_type].items()]
                flattened_units = tuple(set([i for sub in all_units
                                             for i in sub]))
            except KeyError:
                flattened_units = ['1', '%', 'fraction']

            namespace['unit_choices'] = flattened_units
            namespace['unit_type'] = unit_type
        else:
            namespace['unit_choices'] = ['1', '%', 'fraction']
            namespace['unit_type'] = 'Float'

        return super().__new__(cls, name, bases, namespace)


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
    convert_from: str = None
    value: float = None
    min_value: float = None
    max_value: float = None
    standard_deviation: float = None
    replicates: float = None

    def __post_init__(self):
        if hasattr(self.unit, 'decode'):
            self.unit = self.unit.decode('utf-8')

        print(self.__class__.unit_choices)

        if self.unit not in self.__class__.unit_choices:
            raise ValueError('{}: Invalid unit passed in ({})'
                             .format(self.__class__.__name__, repr(self.unit)))

        if self.convert_from is not None:
            self._convert_value_arg()

    def _convert_value_arg(self):
        if hasattr(self.convert_from, 'decode'):
            # ensure we are working with a unicode convert_from value
            self.convert_from = self.convert_from.decode('utf-8')

        if not (self.convert_from in self.__class__.unit_choices and
                self.unit in self.__class__.unit_choices):
            raise ValueError('Invalid conversion from {} to {}'
                             .format(self.convert_from, self.unit))

        for a, v in zip(('value', 'min_value', 'max_value'),
                        (self.value, self.min_value, self.max_value)):
            if v is not None:
                setattr(self, a,
                        convert(self.unit_type,
                                self.convert_from, self.unit, v))

    def to_unit(self, new_unit):
        '''
            Return a FloatUnit object with values converted to the new unit
        '''
        if new_unit not in self.__class__.unit_choices:
            raise ValueError('Invalid conversion from {} to {}'
                             .format(self.unit, new_unit))

        kwargs = {}
        kwargs['unit'] = new_unit

        unit_type = self.unit_type
        if self.unit_type == 'Float':
            # the unit_conversion package has no generic float type,
            # but concentration in water will work pretty in this case
            unit_type = 'Concentration In Water'

        if self.value is not None:
            kwargs['value'] = convert(unit_type, self.unit, new_unit,
                                      self.value)

        if self.min_value is not None:
            kwargs['min_value'] = convert(unit_type, self.unit, new_unit,
                                          self.min_value)

        if self.max_value is not None:
            kwargs['max_value'] = convert(unit_type, self.unit, new_unit,
                                          self.max_value)

        return self.__class__(**kwargs)

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

    def dict(self):
        ret = {}
        for k in self.__dataclass_fields__.keys():
            value = getattr(self, k)
            if value is not None:
                ret[k] = value

        if self.unit_type is not None:
            ret['unit_type'] = self.unit_type

        return ret

    def json(self) -> str:
        return json.dumps(self.dict())


class LengthUnit(FloatUnit):
    pass


class OilConcentrationUnit(FloatUnit):
    pass


class AreaUnit(FloatUnit):
    pass


class VolumeUnit(FloatUnit):
    pass


class TemperatureUnit(FloatUnit):
    pass


#
# This one is not working because the unit type is not syntactically consistent
#
class DeltaTemperatureUnit(FloatUnit):
    pass


class MassUnit(FloatUnit):
    pass


class TimeUnit(FloatUnit):
    pass


class VelocityUnit(FloatUnit):
    pass


class DischargeUnit(FloatUnit):
    pass


class MassDischargeUnit(FloatUnit):
    pass


class DensityUnit(FloatUnit):
    pass


class KinematicViscosityUnit(FloatUnit):
    pass


class DynamicViscosityUnit(FloatUnit):
    pass


class InterfacialTensionUnit(FloatUnit):
    pass


class PressureUnit(FloatUnit):
    pass


class ConcentrationInWaterUnit(FloatUnit):
    pass


class ConcentrationUnit(FloatUnit):
    pass


class DimensionlessUnit(FloatUnit):
    pass


class MassFractionUnit(FloatUnit):
    pass


class VolumeFractionUnit(FloatUnit):
    pass


class AngularMeasureUnit(FloatUnit):
    pass


class AngularVelocityUnit(FloatUnit):
    pass


# lookup table to find a unit class from a unit_type string
UnitClassLU = dict([(camelcase_to_space(k[:-4]), v)
                    for k, v in vars().items()
                    if k.endswith('Unit')])
