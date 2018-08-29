#
# PyMODM model class for Environment Canada's wax
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class Wax(EmbeddedMongoModel):
    fraction = FloatField()
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    standard_deviation = FloatField(blank=True)
    replicates = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(Wax, self).__init__(**kwargs)

    def __repr__(self):
        return ('<Wax('
                'fraction={0.fraction}, '
                'weathering={0.weathering})>'
                .format(self))
