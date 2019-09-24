#
# PyMODM model class for Environment Canada's evaporation equations
# oil properties.
#
import numpy as np

from enum import Enum
from pydantic import BaseModel, constr


class EquationEnum(str, Enum):
    a_bt_ln_t = '(A + BT) ln t'
    a_bt_sqrt_t = '(A + BT) sqrt(t)'
    a_b_ln_t_c = 'A + B ln (t + C)'


class EvaporationEq(BaseModel):
    a: float
    b: float
    c: float
    equation: EquationEnum
    weathering: float = 0.0

    def __post_init_post_parse__(self):
        self.alg = {'(A + BT) ln t': self.calculate_ests_1998,
                    '(A + BT) sqrt(t)': self.calculate_mass_loss1,
                    'A + B ln (t + C)': self.calculate_mass_loss2}

    def calculate(self, t, T=None):
        return self.alg[self.equation](t, T)

    def calculate_ests_1998(self, t, T):
        return (self.a + self.b * T) * np.log(t)

    def calculate_mass_loss1(self, t, T):
        return (self.a + self.b * T) * np.sqrt(t)

    def calculate_mass_loss2(self, t, T):
        return self.a + self.b * np.log(t + self.c)

    def __repr__(self):
        return ('<EvaporationEq(a={0.a}, b={0.b}, c={0.c}, '
                'eq="{0.equation}", '
                'w={0.weathering})>'
                .format(self))
