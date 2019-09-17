#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class ECCut(EmbeddedMongoModel):
    temp_c = FloatField(blank=True)
    percent = FloatField()
    weathering = FloatField(default=0.0)

    method = CharField(max_length=48, blank=True)

    def __init__(self, **kwargs):
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
        return ('<{}({}% at {}C, w={})>'
                .format(self.__class__.__name__,
                        self.percent, self.temp_c, self.weathering))
