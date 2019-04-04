#
# PyMODM model class for Environment Canada's CCME Fractional
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class EcCCMEFraction(EmbeddedMongoModel):
    '''
        CCME Fractions (mg/g oil) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    f1_mg_g = FloatField(blank=True)
    f2_mg_g = FloatField(blank=True)
    f3_mg_g = FloatField(blank=True)
    f4_mg_g = FloatField(blank=True)

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

        super(EcCCMEFraction, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<CCMEFraction('
                'f1={0.f1_mg_g}, '
                'f2={0.f2_mg_g}, '
                'f3={0.f3_mg_g}, '
                'f4={0.f4_mg_g}, '
                'w={0.weathering})>'
                .format(self))
