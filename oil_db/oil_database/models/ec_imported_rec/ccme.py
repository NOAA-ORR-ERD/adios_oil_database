#
# PyMODM model class for Environment Canada's CCME Fractional
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class CCMEFraction(EmbeddedMongoModel):
    '''
        CCME Fractions (mg/g oil) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)

    ccme_f1_mg_g = FloatField(blank=True)
    ccme_f2_mg_g = FloatField(blank=True)
    ccme_f3_mg_g = FloatField(blank=True)
    ccme_f4_mg_g = FloatField(blank=True)

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

        super(CCMEFraction, self).__init__(**kwargs)

    def __repr__(self):
        return ('<CCMEFraction('
                'ccme_f1={0.ccme_f1_mg_g}, '
                'ccme_f2={0.ccme_f2_mg_g}, '
                'ccme_f3={0.ccme_f3_mg_g}, '
                'ccme_f4={0.ccme_f4_mg_g}, '
                'w={0.weathering})>'
                .format(self))


class CCMESaturateCxx(EmbeddedMongoModel):
    '''
        Saturates (F1) (ESTS 2002a)

        Note: This property group seems to be associated to the CCME Fractions,
              so we will define it in the same namespace.
        Note: I am not sure what the units are here, so we don't add any
              suffix to the properties
    '''
    weathering = FloatField(default=0.0)

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
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(CCMESaturateCxx, self).__init__(**kwargs)

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


class CCMEAromaticCxx(CCMESaturateCxx):
    '''
        Aromatics (F2) (ESTS 2002a)
    '''
    def __init__(self, **kwargs):
        super(CCMEAromaticCxx, self).__init__(**kwargs)


class CCMETotalPetroleumCxx(CCMESaturateCxx):
    '''
        GC-TPH (F1 + F2) (ESTS 2002a)
    '''
    total_tph_gc_detected_tph_undetected_tph = FloatField(blank=True)

    def __init__(self, **kwargs):
        super(CCMETotalPetroleumCxx, self).__init__(**kwargs)

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
                'total_tph={0.total_tph_gc_detected_tph_undetected_tph}, '
                'w={0.weathering})>'
                .format(self))
