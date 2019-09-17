#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class ECSARAFraction(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    weathering = FloatField(default=0.0)
    percent = FloatField()

    standard_deviation = FloatField(blank=True)
    replicates = FloatField(blank=True)
    method = CharField(max_length=16, blank=True)

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        # Seriously?  What good is a default if it can't negotiate None values?
        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{}({}={}% w={})>'
                .format(self.__class__.__name__,
                        self.sara_type, self.percent, self.weathering))
