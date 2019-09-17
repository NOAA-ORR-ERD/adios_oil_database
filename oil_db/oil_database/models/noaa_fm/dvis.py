#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class NoaaFmDVis(EmbeddedMongoModel):
    kg_ms = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    method = CharField(max_length=20, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmDVis({0.kg_ms} kg/ms at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))
