#
# PyMODM model class for Environment Canada's biomarker
# oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Biomarkers(BaseModel):
    '''
        Biomarkers (ug/g) (ESTS 2002a)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    c21_tricyclic_terpane: ConcentrationInWaterUnit = None
    c22_tricyclic_terpane: ConcentrationInWaterUnit = None
    c23_tricyclic_terpane: ConcentrationInWaterUnit = None
    c24_tricyclic_terpane: ConcentrationInWaterUnit = None

    _30_norhopane: ConcentrationInWaterUnit = None
    hopane: ConcentrationInWaterUnit = None
    _30_homohopane_22s: ConcentrationInWaterUnit = None
    _30_homohopane_22r: ConcentrationInWaterUnit = None

    _30_31_bishomohopane_22s: ConcentrationInWaterUnit = None
    _30_31_bishomohopane_22r: ConcentrationInWaterUnit = None

    _30_31_trishomohopane_22s: ConcentrationInWaterUnit = None
    _30_31_trishomohopane_22r: ConcentrationInWaterUnit = None

    tetrakishomohopane_22s: ConcentrationInWaterUnit = None
    tetrakishomohopane_22r: ConcentrationInWaterUnit = None

    pentakishomohopane_22s: ConcentrationInWaterUnit = None
    pentakishomohopane_22r: ConcentrationInWaterUnit = None

    _18a_22_29_30_trisnorneohopane: ConcentrationInWaterUnit = None
    _17a_h_22_29_30_trisnorhopane: ConcentrationInWaterUnit = None

    _14b_h_17b_h_20_cholestane: ConcentrationInWaterUnit = None
    _14b_h_17b_h_20_methylcholestane: ConcentrationInWaterUnit = None
    _14b_h_17b_h_20_ethylcholestane: ConcentrationInWaterUnit = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'C21T={0.c21_tricyclic_terpane}, '
                'C22T={0.c22_tricyclic_terpane}, '
                'C23T={0.c23_tricyclic_terpane}, '
                'C24T={0.c24_tricyclic_terpane}, '
                'H29={0._30_norhopane}, '
                'H30={0.hopane}, '
                'H31S={0._30_homohopane_22s}, '
                'H31R={0._30_homohopane_22r}, '
                'H32S={0._30_31_bishomohopane_22s}, '
                'H32R={0._30_31_bishomohopane_22r}, '
                'H33S={0._30_31_trishomohopane_22s}, '
                'H33R={0._30_31_trishomohopane_22r}, '
                'H34S={0.tetrakishomohopane_22s}, '
                'H34R={0.tetrakishomohopane_22r}, '
                'H35S={0.pentakishomohopane_22s}, '
                'H35R={0.pentakishomohopane_22r}, '
                'C27Ts={0._18a_22_29_30_trisnorneohopane}, '
                'C27Tm={0._17a_h_22_29_30_trisnorhopane}, '
                'C27aBB={0._14b_h_17b_h_20_cholestane}, '
                'C28aBB={0._14b_h_17b_h_20_methylcholestane}, '
                'C29aBB={0._14b_h_17b_h_20_ethylcholestane}, '
                'weathering={0.weathering})>'
                .format(self))
