#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class NoaaFmDensity(EmbeddedMongoModel):
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

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

        super(NoaaFmDensity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmDensity({0.kg_m_3} kg/m^3 at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))
