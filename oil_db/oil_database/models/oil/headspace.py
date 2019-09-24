#
# PyMODM model class for headspace oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Headspace(BaseModel):
    '''
        Headspace Analysis (mg/g oil) (ESTS 2002b)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    n_c5: ConcentrationInWaterUnit = None
    n_c6: ConcentrationInWaterUnit = None
    n_c7: ConcentrationInWaterUnit = None
    n_c8: ConcentrationInWaterUnit = None

    c5_group: ConcentrationInWaterUnit = None
    c6_group: ConcentrationInWaterUnit = None
    c7_group: ConcentrationInWaterUnit = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'n_c5={0.n_c5}, '
                'n_c6={0.n_c6}, '
                'n_c7={0.n_c7}, '
                'n_c8={0.n_c8}, '
                'c5_group={0.c5_group}, '
                'c6_group={0.c6_group}, '
                'c7_group={0.c7_group}, '
                'w={0.weathering})>'
                .format(self))
