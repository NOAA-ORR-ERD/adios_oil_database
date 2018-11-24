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
                'weathering={0.weathering})>'
                .format(self))
