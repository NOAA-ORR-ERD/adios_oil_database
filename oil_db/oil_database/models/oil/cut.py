#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.float_unit import TemperatureUnit, FloatUnit


class Cut(EmbeddedMongoModel):
    fraction = EmbeddedDocumentField(FloatUnit)
    liquid_temp = EmbeddedDocumentField(TemperatureUnit, blank=True)
    vapor_temp = EmbeddedDocumentField(TemperatureUnit)
    weathering = FloatField(default=0.0)

    method = CharField(max_length=48, blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(Cut, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'liquid_temp={0.liquid_temp}, '
                'vapor_temp={0.vapor_temp}, '
                'f={0.fraction}, w={0.weathering})>'
                .format(self))
