#
# PyMODM model class for Environment Canada's CCME Fractional
# oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class CCMEFraction(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    '''
        CCME Fractions (mg/g oil) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    f1 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    f2 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    f3 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    f4 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        self._set_embedded_property_args(kwargs)

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<CCMEFraction('
                'f1={0.f1}, '
                'f2={0.f2}, '
                'f3={0.f3}, '
                'f4={0.f4}, '
                'w={0.weathering})>'
                .format(self))


class CarbonNumberDistribution(EmbeddedMongoModel):
    '''
        We have a couple different groups that have similar properties,
        so we will define them here an subclass the groups.

        Note: I am not sure what the units are here, so we don't add any
              suffix to the properties
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    n_c8_to_n_c10 = FloatField(blank=True)
    n_c10_to_n_c12 = FloatField(blank=True)
    n_c12_to_n_c16 = FloatField(blank=True)
    n_c16_to_n_c20 = FloatField(blank=True)
    n_c20_to_n_c24 = FloatField(blank=True)
    n_c24_to_n_c28 = FloatField(blank=True)
    n_c28_to_n_c34 = FloatField(blank=True)
    n_c34 = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'n_c8_to_c10={0.n_c8_to_n_c10}, '
                'n_c10_to_c12={0.n_c10_to_n_c12}, '
                'n_c12_to_c16={0.n_c12_to_n_c16}, '
                'n_c16_to_c20={0.n_c16_to_n_c20}, '
                'n_c20_to_c24={0.n_c20_to_n_c24}, '
                'n_c24_to_c28={0.n_c24_to_n_c28}, '
                'n_c28_to_c34={0.n_c28_to_n_c34}, '
                'n_c34={0.n_c34}, '
                'w={0.weathering})>'
                .format(self))


class CCMESaturateCxx(CarbonNumberDistribution):
    '''
        Saturates (F1) (ESTS 2002a)

        Note: The Cxx property groups seem to be associated with the
              CCME Fractions, so we will define them in the same namespace.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CCMEAromaticCxx(CarbonNumberDistribution):
    '''
        Aromatics (F2) (ESTS 2002a)
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CCMETotalPetroleumCxx(CarbonNumberDistribution):
    '''
        GC-TPH (F1 + F2) (ESTS 2002a)
    '''
    total_tph_gc_detected_tph_undetected_tph = FloatField(blank=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
