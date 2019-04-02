#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.float_unit import TemperatureUnit


class DVis(EmbeddedMongoModel):
    mpa_s = FloatField()
    ref_temp = EmbeddedDocumentField(TemperatureUnit)
    weathering = FloatField(default=0.0)

    method = CharField(max_length=32, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(DVis, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.mpa_s} mPa.s at {0.ref_temp}, w={0.weathering})>'
                .format(self))
