#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin
from oil_database.models.common.float_unit import (TemperatureUnit,
                                                   DynamicViscosityUnit)


class DVis(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    viscosity = EmbeddedDocumentField(DynamicViscosityUnit)
    ref_temp = EmbeddedDocumentField(TemperatureUnit)
    weathering = FloatField(default=0.0)

    method = CharField(max_length=32, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        self._set_embedded_property_args(kwargs)

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.viscosity} at {0.ref_temp}, w={0.weathering})>'
                .format(self))
