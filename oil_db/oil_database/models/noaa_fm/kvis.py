#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class NoaaFmKVis(EmbeddedMongoModel):
    m_2_s = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(NoaaFmKVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmKVis({0.m_2_s} m^2/s at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))
