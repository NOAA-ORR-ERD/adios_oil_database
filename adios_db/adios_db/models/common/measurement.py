'''
Generic Measurement Types

These are structures that handle an individual measurment:

They have a value, a unit type and a unit.

They can be converted to other units if need be.

They can accommodate a single value, or a range of values

They can also accommodate a standard deviation and number of replicates.
'''

from dataclasses import dataclass, asdict
from math import isclose
import copy

from unit_conversion import convert

from ..common.utilities import dataclass_to_json
from ..common.validators import EnumValidator

# why are these oil specific???
# There should be a project-wide repository for warnings & errors

from ..oil.validation.warnings import WARNINGS
from ..oil.validation.errors import ERRORS

__all__ = ['AngularVelocity',
           'Concentration',
           'Density',
           'Dimensionless',
           'DynamicViscosity',
           'InterfacialTension',
           'KinematicViscosity',
           'Length',
           'Mass',
           'MassFraction',
           'VolumeFraction',
           'NeedleAdhesion',
           'Pressure',
           'Temperature',
           'Time',
           'Unitless',
           ]

# fixme: why is this here?
# it should be in validation, and the list itself should probably
# be in a data file or something.
# class ProductType(str):
#     _valid_types = ('crude',
#                     'refined',
#                     'bitumen product',
#                     'other')
#     _validator = EnumValidator(_valid_types, WARNINGS["W003"],
#                                case_insensitive=True)

#     def validate(self):
#         return self._validator(self)


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

       (there is a __post_init, but it's not getting used for some reason)

       Also: None should not be an option for unit, either.

       Fixme: maybe there could be a default unit for each unit type?
    """
    value: float = None
    unit: str = None
    min_value: float = None
    max_value: float = None
    standard_deviation: float = None
    replicates: int = None
    unit_type: str = None

    def __post_init__(self):
        """
        this here so that it can get overidden in subclasses

        it appears dataclasses don't add it to __init__ unless it's here
        """
        pass
        # if all((attr is None)
        #        for attr in (self.value, self.min_value, self.max_value)):
        #     raise TypeError(f'{self.__class__.__name__}(): '
        #                      'expected at least one value')

    #     # if self.unit is None:
    #     #     raise TypeError:(f'{self.__class__.__name__}(): '
    #     #                      'expected a unit')

    # # We want a less-noisy repr
    # def __repr__(self):
    #     atts = ((att, getattr(self, att)) for att in self.__dataclass_fields__.keys())
    #     atts = (f'{att}={val}' for att, val in atts if val is not None)
    #     return f'{self.__class__.__name__}({", ".join(atts)})'

    # __str__ = __repr__


class MeasurementBase(MeasurementDataclass):
    # need to add these here, so they won't be overwritten by the
    # decorator
    unit_type = None

    def __post_init__(self):
        if self.__class__.unit_type is None:
            raise NotImplementedError("Can't initialize a measurement with no unit_type")
        if self.unit_type is None:
            self.unit_type = self.__class__.unit_type
        self.unit_type = self.unit_type.lower()
        if self.unit_type != self.__class__.unit_type:
            raise ValueError(f"unit_type must be: {self.__class__.unit_type}, not {self.unit_type}")
        super().__post_init__()

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
        # fixme: why not use the copy.deepcopy() function here?

        return copy.copy(self)


class Temperature(MeasurementBase):
    unit_type = "temperature"
    fixCK = False  # you can monkey-patch this to turn it on.

    def __post_init__(self):
        super().__post_init__()
        if self.fixCK:
            self.fix_C_K()

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

    def validate(self):
        msgs = []
        if self is None:  # how can this happen?!?!
            return msgs
        # only do this for C or K
        if self.unit.upper() not in {'C', 'K'}:
            return msgs
        for val in (self.value, self.min_value, self.max_value):
            if val is not None:
                val_in_C = convert(self.unit, "C", val)
                decimal = val_in_C % 1
                if isclose(decimal, 0.15) or isclose(decimal, 0.85):
                    msgs.append(WARNINGS['W010'].format(f"{val:.2f} {self.unit} ({val_in_C:.2f} C)",
                                                        f"{round(val_in_C):.2f} C"))
        return msgs

    def fix_C_K(self):
        """
        This is a bit of a kludge:

        The correct conversion from C to K is 273.16

        But a lot of data sources (notably the ADIOS2 database)
        used 273.0.

        So we end up with temps like: -0.15 C instead of 0.0 C
        This function will "correct" that.

        Note: it also converts to C
        """
        # only do this if there's a validation issue
        for msg in self.validate():
            if 'W010:' in msg:
                break
        else:  # no issue found
            return

        # convert to C
        self.convert_to('C')
        for attr in ("value", "min_value", "max_value"):
            val = getattr(self, attr)
            if val is not None:
                decimal = val % 1
                if isclose(decimal, 0.15) or isclose(decimal, 0.85):
                    setattr(self, attr, round(val))
        return


class Unitless(MeasurementBase):
    '''
    This is a type for data with no unit at all.
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


class Concentration(MeasurementBase):
    unit_type = 'concentration'


class MassFraction(MeasurementBase):
    unit_type = "massfraction"
    # add a validator: should be between 0 and 1.0


class VolumeFraction(MeasurementBase):
    unit_type = "volumefraction"
    # add a validator: should be between 0 and 1.0

@dataclass
class MassOrVolumeFraction(MeasurementBase):
    """
    This could be Mass or Volume Fraction, needs to be specified

    :param unit_type: the value itself
    :param value: the value itself
    :param unit: the value itself
    :param min_value: the value itself
    :param max_value: the value itself
    :param standard_deviation: the value itself
    :param replicates: the value itself
    :param unit_type: the type of unit -- must be "massfraction" or "volumefraction"
    """

    def __init__(self, unit_type=None, *args, **kwargs):
        if unit_type is None:
            raise TypeError("unit_type must be specified")
        try:
            unit_type = unit_type.lower()
            if unit_type not in {'massfraction', 'volumefraction'}:
                raise AttributeError
        except AttributeError:
            raise ValueError("unit_type must be one of: 'massfraction', 'volumefraction'")
        # self.__dict__['unit_type'] = unit_type
        kwargs['unit_type'] = unit_type
        super().__init__(*args, **kwargs)

    def __post_init__(self):
        # We don't need the post_init in this case
        pass

    def copy(self):
        '''
        copy an instance

        This needs to be special, to preserve the unit_type attribute
        '''
        # fixme: this should probably be the __copy__ method

        return copy.copy(self)

    def __eq__(self, other):
        return super().__eq__(other) and (self.unit_type == other.unit_type)



class Density(MeasurementBase):
    unit_type = "density"


class DynamicViscosity(MeasurementBase):
    unit_type = "dynamicviscosity"


class KinematicViscosity(MeasurementBase):
    unit_type = "kinematicviscosity"


class Pressure(MeasurementBase):
    unit_type = "pressure"


class NeedleAdhesion(MeasurementBase):
    unit_type = "needleadhesion"


class InterfacialTension(MeasurementBase):
    unit_type = "interfacialtension"


class AngularVelocity(MeasurementBase):
    unit_type = 'angularvelocity'
