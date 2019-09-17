#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class NoaaFmCut(EmbeddedMongoModel):
    vapor_temp_k = FloatField(blank=True)
    liquid_temp_k = FloatField(blank=True)
    fraction = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(NoaaFmCut, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        lt = '{}K'.format(self.liquid_temp_k) if self.liquid_temp_k else None
        vt = '{}K'.format(self.vapor_temp_k) if self.vapor_temp_k else None
        return ('<NoaaFmCut(liquid_temp={}, vapor_temp={}, fraction={}, w={})>'
                .format(lt, vt, self.fraction, self.weathering))
