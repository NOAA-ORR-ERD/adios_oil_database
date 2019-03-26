#
# PyMODM model class for Environment Canada's flash point
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import (CharField,
                           FloatField)


class ECFlashPoint(EmbeddedMongoModel):
    min_temp_c = FloatField(blank=True)
    max_temp_c = FloatField(blank=True)
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    standard_deviation = FloatField(blank=True)
    replicates = FloatField(blank=True)
    method = CharField(max_length=32, blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        if len(kwargs.keys()) > 0:
            for a, _v in kwargs.items():
                if (a not in self.__class__.__dict__):
                    del kwargs[a]

            if 'weathering' not in kwargs or kwargs['weathering'] is None:
                # Seriously?  What good is a default if it can't negotiate
                # None values?
                kwargs['weathering'] = 0.0

        super(ECFlashPoint, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        min_temp = self.min_temp_c
        max_temp = self.max_temp_c
        w = self.weathering

        return ('<{}([{}{}, {}{}], w={})>'
                .format(self.__class__.__name__,
                        min_temp, '' if min_temp is None else 'C',
                        max_temp, '' if max_temp is None else 'C',
                        w))
