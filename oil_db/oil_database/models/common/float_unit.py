#
# PyMODM Model class definitions for embedded content in our oil records
#
from itertools import izip_longest

from unit_conversion.unit_data import ConvertDataUnits

from pymodm.base.models import MongoModelMetaclass
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class UnitMeta(MongoModelMetaclass):
    def __new__(cls, name, bases, dct):
        # we will only try this if we are a 'Unit' type class
        max_length = 32

        if name.endswith('Unit'):
            unit_field = cls.camelcase_to_space(name[:-4])
            try:
                all_units = [[k] + v[1]
                             for k, v
                             in ConvertDataUnits[unit_field].iteritems()]
                flattened_units = tuple(set([i for sub in all_units
                                             for i in sub]))

                dct['unit'] = CharField(max_length=max_length,
                                        choices=flattened_units)
            except KeyError:
                dct['unit'] = CharField(max_length=max_length)
        else:
            dct['unit'] = CharField(max_length=max_length)

        return super(UnitMeta, cls).__new__(cls, name, bases, dct)

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
                for (begin, end) in izip_longest(idxs, idxs[1:])]


class FloatUnit(EmbeddedMongoModel):
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
    __metaclass__ = UnitMeta
    value = FloatField()

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(FloatUnit, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.unit in (None, '1'):
            return (u'<{}({})>'
                    .format(self.__class__.__name__, self.value)
                    .encode('utf-8'))
        else:
            return (u'<{}({} {})>'
                    .format(self.__class__.__name__, self.value, self.unit)
                    .encode('utf-8'))


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
