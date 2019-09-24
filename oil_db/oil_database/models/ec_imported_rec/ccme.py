#
# Model class for Environment Canada's CCME Fractional
# oil properties.
#
from pydantic import BaseModel, constr


class EcCCMEFraction(BaseModel):
    '''
        CCME Fractions (mg/g oil) (ESTS 2002a)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    f1_mg_g: float = None
    f2_mg_g: float = None
    f3_mg_g: float = None
    f4_mg_g: float = None

    def __repr__(self):
        return ('<CCMEFraction('
                'f1={0.f1_mg_g}, '
                'f2={0.f2_mg_g}, '
                'f3={0.f3_mg_g}, '
                'f4={0.f4_mg_g}, '
                'w={0.weathering})>'
                .format(self))
