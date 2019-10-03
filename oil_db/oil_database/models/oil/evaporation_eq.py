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
    c: float = None
    equation: EquationEnum
    weathering: float = 0.0

    _alg: dict = None

    def __init__(self, **data):
        super().__init__(**data)

        self.__post_init_post_parse__()

    def __post_init_post_parse__(self):
        self._alg = {'(A + BT) ln t': self.calculate_ests_1998,
                     '(A + BT) sqrt(t)': self.calculate_mass_loss1,
                     'A + B ln (t + C)': self.calculate_mass_loss2}

    def __setattr__(self, name, value):
        '''
            Are there any dataclass packages that don't have at least one
            annoyance?
            pydantic doesn't accept attributes as fields if they start with
            an underscore.
            This sucks for PyMongo, since the default identifier is _id
        '''
        if name == '_alg':
            self.__dict__[name] = value
        else:
            super().__setattr__(name, value)

    def calculate(self, t, T=None):
        return self._alg[self.equation](t, T)

    def calculate_ests_1998(self, t, T):
        return (self.a + self.b * T) * np.log(t)

    def calculate_mass_loss1(self, t, T):
        return (self.a + self.b * T) * np.sqrt(t)

    def calculate_mass_loss2(self, t, T):
        return self.a + self.b * np.log(t + self.c)

    def dict(self, **kwargs) -> 'DictStrAny':
        '''
            Overloaded version of BaseModel.dict(), which adds the
            expand_refs argument.
        '''
        res = super().dict(**kwargs)
        res['_cls'] = '{}.{}'.format(self.__class__.__module__,
                                     self.__class__.__name__)
        del res['_alg']

        return res

    def __repr__(self):
        return ('<EvaporationEq(a={0.a}, b={0.b}, c={0.c}, '
                'eq="{0.equation}", '
                'w={0.weathering})>'
                .format(self))
