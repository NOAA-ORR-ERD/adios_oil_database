#
# PyMODM model class for Environment Canada's evaporation equations
# oil properties.
#
import numpy as np

from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField, CharField


class EvaporationEq(EmbeddedMongoModel):
    a = FloatField()
    b = FloatField()
    c = FloatField()
    equation = CharField(choices=('(A + BT) ln t',
                                  '(A + BT) sqrt(t)',
                                  'A + B ln (t + C)'))
    weathering = FloatField(default=0.0)

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

        super(EvaporationEq, self).__init__(**kwargs)

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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<EvaporationEq(a={0.a}, b={0.b}, c={0.c}, '
                'eq="{0.equation}", '
                'w={0.weathering})>'
                .format(self))
