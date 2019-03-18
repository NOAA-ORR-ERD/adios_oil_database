#
# PyMODM model class for Environment Canada's benzene
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField, CharField


class Benzene(EmbeddedMongoModel):
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    benzene_ppm = FloatField(blank=True)
    toluene_ppm = FloatField(blank=True)
    ethylbenzene_ppm = FloatField(blank=True)
    m_p_xylene_ppm = FloatField(blank=True)
    o_xylene_ppm = FloatField(blank=True)

    isopropylbenzene_ppm = FloatField(blank=True)
    propylebenzene_ppm = FloatField(blank=True)
    isobutylbenzene_ppm = FloatField(blank=True)
    amylbenzene_ppm = FloatField(blank=True)
    n_hexylbenzene_ppm = FloatField(blank=True)

    _1_2_3_trimethylbenzene_ppm = FloatField(blank=True)
    _1_2_4_trimethylbenzene_ppm = FloatField(blank=True)
    _1_2_dimethyl_4_ethylbenzene_ppm = FloatField(blank=True)
    _1_3_5_trimethylbenzene_ppm = FloatField(blank=True)
    _1_methyl_2_isopropylbenzene_ppm = FloatField(blank=True)
    _2_ethyltoluene_ppm = FloatField(blank=True)
    _3_4_ethyltoluene_ppm = FloatField(blank=True)

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

        super(Benzene, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<Benzene('
                'benzene={0.benzene_ppm}ppm, '
                'w={0.weathering})>'
                .format(self))
