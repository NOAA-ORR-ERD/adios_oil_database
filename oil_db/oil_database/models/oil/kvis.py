#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class KVis(EmbeddedMongoModel):
    m_2_s = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(KVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.m_2_s} m^2/s at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))
