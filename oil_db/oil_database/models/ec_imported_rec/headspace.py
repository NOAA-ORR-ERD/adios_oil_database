#
# PyMODM model class for Environment Canada's headspace
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class ECHeadspace(EmbeddedMongoModel):
    '''
        Headspace Analysis (mg/g oil) (ESTS 2002b)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    n_c5_mg_g = FloatField(blank=True)
    n_c6_mg_g = FloatField(blank=True)
    n_c7_mg_g = FloatField(blank=True)
    n_c8_mg_g = FloatField(blank=True)

    c5_group_mg_g = FloatField(blank=True)
    c6_group_mg_g = FloatField(blank=True)
    c7_group_mg_g = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'n_c5={0.n_c5_mg_g}, '
                'n_c6={0.n_c6_mg_g}, '
                'n_c7={0.n_c7_mg_g}, '
                'n_c8={0.n_c8_mg_g}, '
                'c5_group={0.c5_group_mg_g}, '
                'c6_group={0.c6_group_mg_g}, '
                'c7_group={0.c7_group_mg_g}, '
                'w={0.weathering})>'
                .format(self))
