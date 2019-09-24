#
# PyMODM model class for Environment Canada's CCME Fractional
# oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class CCMEFraction(BaseModel):
    '''
        CCME Fractions (mg/g oil) (ESTS 2002a)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    f1: ConcentrationInWaterUnit = None
    f2: ConcentrationInWaterUnit = None
    f3: ConcentrationInWaterUnit = None
    f4: ConcentrationInWaterUnit = None

    def __repr__(self):
        return ('<CCMEFraction('
                'f1={0.f1}, '
                'f2={0.f2}, '
                'f3={0.f3}, '
                'f4={0.f4}, '
                'w={0.weathering})>'
                .format(self))


class CarbonNumberDistribution(BaseModel):
    '''
        We have a couple different groups that have similar properties,
        so we will define them here an subclass the groups.

        Note: I am not sure what the units are here, so we don't add any
              suffix to the properties
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    n_c8_to_n_c10: float = None
    n_c10_to_n_c12: float = None
    n_c12_to_n_c16: float = None
    n_c16_to_n_c20: float = None
    n_c20_to_n_c24: float = None
    n_c24_to_n_c28: float = None
    n_c28_to_n_c34: float = None
    n_c34: float = None

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
    total_tph_gc_detected_tph_undetected_tph: float = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
