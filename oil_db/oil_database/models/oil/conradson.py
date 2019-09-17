from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import FloatField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin
from oil_database.models.common.float_unit import FloatUnit


class Conradson(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    weathering = FloatField(default=0.0)

    residue = EmbeddedDocumentField(FloatUnit, blank=True)
    crude = EmbeddedDocumentField(FloatUnit, blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        self._set_embedded_property_args(kwargs)

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{}(residue={}, crude={}, w={})>'
                .format(self.__class__.__name__,
                        self.residue, self.crude, self.weathering))
