#
# PyMODM model class for Environment Canada's n-Alkane
# oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class NAlkanes(BaseModel):
    '''
        n-Alkanes (ug/g oil) (ESTS 2002a)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    pristane: ConcentrationInWaterUnit = None
    phytane: ConcentrationInWaterUnit = None
    c8: ConcentrationInWaterUnit = None
    c9: ConcentrationInWaterUnit = None
    c10: ConcentrationInWaterUnit = None
    c11: ConcentrationInWaterUnit = None
    c12: ConcentrationInWaterUnit = None
    c13: ConcentrationInWaterUnit = None
    c14: ConcentrationInWaterUnit = None
    c15: ConcentrationInWaterUnit = None
    c16: ConcentrationInWaterUnit = None
    c17: ConcentrationInWaterUnit = None
    c18: ConcentrationInWaterUnit = None
    c19: ConcentrationInWaterUnit = None
    c20: ConcentrationInWaterUnit = None
    c21: ConcentrationInWaterUnit = None
    c22: ConcentrationInWaterUnit = None
    c23: ConcentrationInWaterUnit = None
    c24: ConcentrationInWaterUnit = None
    c25: ConcentrationInWaterUnit = None
    c26: ConcentrationInWaterUnit = None
    c27: ConcentrationInWaterUnit = None
    c28: ConcentrationInWaterUnit = None
    c29: ConcentrationInWaterUnit = None
    c30: ConcentrationInWaterUnit = None
    c31: ConcentrationInWaterUnit = None
    c32: ConcentrationInWaterUnit = None
    c33: ConcentrationInWaterUnit = None
    c34: ConcentrationInWaterUnit = None
    c35: ConcentrationInWaterUnit = None
    c36: ConcentrationInWaterUnit = None
    c37: ConcentrationInWaterUnit = None
    c38: ConcentrationInWaterUnit = None
    c39: ConcentrationInWaterUnit = None
    c40: ConcentrationInWaterUnit = None
    c41: ConcentrationInWaterUnit = None
    c42: ConcentrationInWaterUnit = None
    c43: ConcentrationInWaterUnit = None
    c44: ConcentrationInWaterUnit = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'pristane={0.pristane}, '
                'phytane={0.phytane}, '
                'c8={0.c8}, '
                'c9={0.c9}, '
                'c10={0.c10}, '
                'c11={0.c11}, '
                'c12={0.c12}, '
                'c13={0.c13}, '
                'c14={0.c14}, '
                'c15={0.c15}, '
                'c16={0.c16}, '
                'c17={0.c17}, '
                'c18={0.c18}, '
                'c19={0.c19}, '
                'c20={0.c20}, '
                'c21={0.c21}, '
                'c22={0.c22}, '
                'c23={0.c23}, '
                'c24={0.c24}, '
                'c25={0.c25}, '
                'c26={0.c26}, '
                'c27={0.c27}, '
                'c28={0.c28}, '
                'c29={0.c29}, '
                'c30={0.c30}, '
                'c31={0.c31}, '
                'c32={0.c32}, '
                'c33={0.c33}, '
                'c34={0.c34}, '
                'c35={0.c35}, '
                'c36={0.c36}, '
                'c37={0.c37}, '
                'c38={0.c38}, '
                'c39={0.c39}, '
                'c40={0.c40}, '
                'c41={0.c41}, '
                'c42={0.c42}, '
                'c43={0.c43}, '
                'c44={0.c44}, '
                'weathering={0.weathering})>'
                .format(self))
