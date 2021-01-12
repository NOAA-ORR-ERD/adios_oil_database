'''
    Generic Unitted Types
    these are structures that contain a floating point value and an associated
    unit
'''
from dataclasses import dataclass, asdict

from unit_conversion import convert

from ..common.utilities import dataclass_to_json
from ..common.validators import EnumValidator

# why are these oil specific???
# There should be a project-wide repository for warnings & errors

from ..oil.validation.warnings import WARNINGS
from ..oil.validation.errors import ERRORS


# fixme: why is this here?
# it should be in validation, and the list itself should probably
# be in a data file or something.
class ProductType(str):
    _valid_types = ('crude',
                    'refined',
                    'bitumen product',
                    'other')
    _validator = EnumValidator(_valid_types, WARNINGS["W003"],
                               case_insensitive=True)

    def validate(self):
        return self._validator(self)


@dataclass_to_json
@dataclass
class UnittedValue:
    """
    Data structure to hold a value with a unit

    This accommodates both a single value and a range of values

    There is some complexity here, so everything is optional

    But maybe it would be better to have some validation on creation

    NOTES:
       If there is a value, there should be no min_value or max_value
       If there is only  a min or max, then it is interpreted as
       greater than or less than
    """
    value: float = None
    min_value: float = None
    max_value: float = None
    unit: str = None
    # unit_type: str = None

    def __post_init__(self):
        if all((attr is None)
               for attr in (self.value, self.min_value, self.max_value)):
            raise ValueError(f'{self.__class__.__name__}(): '
                             'need to supply a value')

        if self.unit is None:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'need to supply a unit')


@dataclass_to_json
@dataclass
class UnittedRange:
    """
    Data structure to hold a range of values with a unit

    This differs from UnittedValue in that it Always is a range
    with no single value option

    """
    min_value: float = None
    max_value: float = None
    unit: str = None


@dataclass_to_json
@dataclass
class MeasurementDataclass:
    """
    Data structure to hold a value with a unit

    This accommodates both a single value and a range of values

    There is some complexity here, so everything is optional

    But maybe it would be better to have some validation on creation

    NOTES:
       If there is a value, there should be no min_value or max_value
       If there is only  a min or max, then it is interpreted as
       greater than or less than

       There needs to be validation on that!
    """
    value: float = None
    unit: str = None
    min_value: float = None
    max_value: float = None
    standard_deviation: float = None
    replicates: float = None


class MeasurementBase(MeasurementDataclass):
    # need to add these here, so they won't be overwritten by the
    # decorator
    unit_type = None

    def __post_init__(self):
        if all((attr is None)
               for attr in (self.value, self.min_value, self.max_value)):
            raise ValueError(f'{self.__class__.__name__}(): '
                             'need to supply a value')

        if self.unit is None:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'need to supply a unit')

    def py_json(self, sparse=True):
        # unit_type is added here, as it's not a settable field
        pj = super().py_json(sparse)
        pj['unit_type'] = self.unit_type

        return pj

    def convert_to(self, new_unit):
        """
        Convert this Measurement object to the specified new unit

        The object is mutated in place.

        If the conversion can not be performed, an Exception will
        be raised, and the object not altered.

        This will also return the object (self) -- but that is a
        deprecated feature -- do not use it!

        If you want a new object, use `converted_to` instead
        """

        new_vals = {att: None for att in ('value', 'min_value', 'max_value',
                                          'standard_deviation')}

        for attr in new_vals.keys():
            val = getattr(self, attr)

            if val is not None:
                new_val = convert(self.unit_type,
                                  self.unit,
                                  new_unit,
                                  val)
                new_vals[attr] = new_val

        # if this was all successful
        new_vals['unit'] = new_unit

        self.__dict__.update(new_vals)

        return None

    def converted_to(self, new_unit):
        """
        returns a new Measurement object, converted to the units specified
        """
        new = self.copy()
        new.convert_to(new_unit)
        return new

    def copy(self):
        '''
            There will be cases where we want to be non-destructive, such as
            a function that needs to convert to different units to perform
            calculations, but return the results in the original units.

            And since our convert function does an in-place update, we will
            need a way to preserve the original contents of our dataclass
            before the conversion happens.
        '''
        return self.__class__(**asdict(self))


class Temperature(MeasurementBase):
    unit_type = "temperature"

    def convert_to(self, new_unit):
        # need to do the "right thing" with standard deviation
        if self.standard_deviation is None:
            # no need for anything special
            super().convert_to(new_unit)
        else:
            new_std = convert("deltatemperature",
                              self.unit,
                              new_unit,
                              self.standard_deviation)
            super().convert_to(new_unit)
            self.standard_deviation = new_std

        return self


class Unitless(MeasurementBase):
    '''
        This is a type that has no unit at all.
    '''
    unit_type = "unitless"

    def convert_to(self, *args, **kwargs):
        raise TypeError("You can not convert a Unitless measurement")


class Dimensionless(MeasurementBase):
    '''
        This is a type that can be converted to generic fractional amounts,
        but does not refer to a particular measurable quantity.
    '''
    unit_type = "dimensionless"


class Time(MeasurementBase):
    unit_type = "time"


class Length(MeasurementBase):
    unit_type = "length"


class Mass(MeasurementBase):
    unit_type = "mass"


class MassFraction(MeasurementBase):
    unit_type = "massfraction"


class VolumeFraction(MeasurementBase):
    unit_type = "volumefraction"


class Density(MeasurementBase):
    unit_type = "density"


class DynamicViscosity(MeasurementBase):
    unit_type = "dynamicviscosity"


class KinematicViscosity(MeasurementBase):
    unit_type = "kinematicviscosity"


class Pressure(MeasurementBase):
    unit_type = "pressure"


class NeedleAdhesion(MeasurementBase):
    unit_type = None


class InterfacialTension(MeasurementBase):
    unit_type = "interfacialtension"


class AngularVelocity(MeasurementBase):
    unit_type = 'angularvelocity'