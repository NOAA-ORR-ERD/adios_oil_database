#
# PyMODM model class for Environment Canada's n-Alkane
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class ECNAlkanes(EmbeddedMongoModel):
    '''
        n-Alkanes (ug/g oil) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    pristane_ug_g = FloatField(blank=True)
    phytane_ug_g = FloatField(blank=True)
    c8_ug_g = FloatField(blank=True)
    c9_ug_g = FloatField(blank=True)
    c10_ug_g = FloatField(blank=True)
    c11_ug_g = FloatField(blank=True)
    c12_ug_g = FloatField(blank=True)
    c13_ug_g = FloatField(blank=True)
    c14_ug_g = FloatField(blank=True)
    c15_ug_g = FloatField(blank=True)
    c16_ug_g = FloatField(blank=True)
    c17_ug_g = FloatField(blank=True)
    c18_ug_g = FloatField(blank=True)
    c19_ug_g = FloatField(blank=True)
    c20_ug_g = FloatField(blank=True)
    c21_ug_g = FloatField(blank=True)
    c22_ug_g = FloatField(blank=True)
    c23_ug_g = FloatField(blank=True)
    c24_ug_g = FloatField(blank=True)
    c25_ug_g = FloatField(blank=True)
    c26_ug_g = FloatField(blank=True)
    c27_ug_g = FloatField(blank=True)
    c28_ug_g = FloatField(blank=True)
    c29_ug_g = FloatField(blank=True)
    c30_ug_g = FloatField(blank=True)
    c31_ug_g = FloatField(blank=True)
    c32_ug_g = FloatField(blank=True)
    c33_ug_g = FloatField(blank=True)
    c34_ug_g = FloatField(blank=True)
    c35_ug_g = FloatField(blank=True)
    c36_ug_g = FloatField(blank=True)
    c37_ug_g = FloatField(blank=True)
    c38_ug_g = FloatField(blank=True)
    c39_ug_g = FloatField(blank=True)
    c40_ug_g = FloatField(blank=True)
    c41_ug_g = FloatField(blank=True)
    c42_ug_g = FloatField(blank=True)
    c43_ug_g = FloatField(blank=True)
    c44_ug_g = FloatField(blank=True)

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
        return ('<ECNAlkanes('
                'pristane={0.pristane_ug_g}, '
                'phytane={0.phytane_ug_g}, '
                'c8={0.c8_ug_g}, '
                'c9={0.c9_ug_g}, '
                'c10={0.c10_ug_g}, '
                'c11={0.c11_ug_g}, '
                'c12={0.c12_ug_g}, '
                'c13={0.c13_ug_g}, '
                'c14={0.c14_ug_g}, '
                'c15={0.c15_ug_g}, '
                'c16={0.c16_ug_g}, '
                'c17={0.c17_ug_g}, '
                'c18={0.c18_ug_g}, '
                'c19={0.c19_ug_g}, '
                'c20={0.c20_ug_g}, '
                'c21={0.c21_ug_g}, '
                'c22={0.c22_ug_g}, '
                'c23={0.c23_ug_g}, '
                'c24={0.c24_ug_g}, '
                'c25={0.c25_ug_g}, '
                'c26={0.c26_ug_g}, '
                'c27={0.c27_ug_g}, '
                'c28={0.c28_ug_g}, '
                'c29={0.c29_ug_g}, '
                'c30={0.c30_ug_g}, '
                'c31={0.c31_ug_g}, '
                'c32={0.c32_ug_g}, '
                'c33={0.c33_ug_g}, '
                'c34={0.c34_ug_g}, '
                'c35={0.c35_ug_g}, '
                'c36={0.c36_ug_g}, '
                'c37={0.c37_ug_g}, '
                'c38={0.c38_ug_g}, '
                'c39={0.c39_ug_g}, '
                'c40={0.c40_ug_g}, '
                'c41={0.c41_ug_g}, '
                'c42={0.c42_ug_g}, '
                'c43={0.c43_ug_g}, '
                'c44={0.c44_ug_g}, '
                'weathering={0.weathering})>'
                .format(self))
