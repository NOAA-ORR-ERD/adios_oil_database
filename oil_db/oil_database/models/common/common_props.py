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
                all_units = [i for sub
                             in [[k] + v[1]
                                 for k, v
                                 in ConvertDataUnits[unit_field].iteritems()]
                             for i in sub]

                dct['unit'] = CharField(max_length=max_length,
                                        choices=tuple(set(all_units)))
                # print (dct['unit'].choices)
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


class Synonym(EmbeddedMongoModel):
    name = CharField(max_length=40)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(Synonym, self).__init__(**kwargs)

    def __repr__(self):
        return "<Synonym('%s')>" % (self.name)


class Density(EmbeddedMongoModel):
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(Density, self).__init__(**kwargs)

    def __repr__(self):
        return ('<Density({0.kg_m_3} kg/m^3 at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))


class KVis(EmbeddedMongoModel):
    m_2_s = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(KVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<KVis({0.m_2_s} m^2/s at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))


class DVis(EmbeddedMongoModel):
    kg_ms = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    method = CharField(max_length=20, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(DVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<DVis({0.kg_ms} kg/ms at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))


class Cut(EmbeddedMongoModel):
    vapor_temp_k = FloatField(blank=True)
    liquid_temp_k = FloatField(blank=True)
    fraction = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(Cut, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        lt = '{}K'.format(self.liquid_temp_k) if self.liquid_temp_k else None
        vt = '{}K'.format(self.vapor_temp_k) if self.vapor_temp_k else None
        return ('<Cut(liquid_temp={}, vapor_temp={}, fraction={}, w={})>'
                .format(lt, vt, self.fraction, self.weathering))


class Toxicity(EmbeddedMongoModel):
    tox_type = CharField(choices=('EC', 'LC'))
    species = CharField(max_length=24)
    after_24h = FloatField(blank=True)
    after_48h = FloatField(blank=True)
    after_96h = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(Toxicity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<Toxicity({0.species}, {0.tox_type}, '
                '[{0.after_24h}, {0.after_48h}, {0.after_96h}])>'
                .format(self))


class SARAFraction(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    fraction = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    standard_deviation = FloatField(blank=True)
    replicates = FloatField(blank=True)
    method = CharField(max_length=16, blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        # Seriously?  What good is a default if it can't negotiate None values?
        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        if 'ref_temp_k' not in kwargs or kwargs['ref_temp_k'] is None:
            kwargs['ref_temp_k'] = 273.15

        super(SARAFraction, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<SARAFraction({0.sara_type}={0.fraction} '
                'at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))


class SARADensity(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(SARADensity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<SARADensity('
                '{0.sara_type}={0.kg_m_3} kg/m^3 at {0.ref_temp_k}K)>'
                .format(self))


class MolecularWeight(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    g_mol = FloatField()
    ref_temp_k = FloatField()

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(MolecularWeight, self).__init__(**kwargs)

    @property
    def kg_mol(self):
        return self.g_mol / 1000.0

    @kg_mol.setter
    def length(self, value):
        self.g_mol = value * 1000.0

    def __repr__(self):
        return ('<MolecularWeight('
                '{0.sara_type}={0.g_mol} gm/mol at {0.ref_temp_k}K)>'
                .format(self))
