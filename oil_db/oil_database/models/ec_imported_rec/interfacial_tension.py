#
# PyMODM model class for Environment Canada's interfacial tension
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import (CharField,
                           FloatField)


class InterfacialTension(EmbeddedMongoModel):
    interface = CharField(choices=('air', 'water', 'seawater'))
    n_m = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    method = CharField(max_length=32, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

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

        super(InterfacialTension, self).__init__(**kwargs)

    def __repr__(self):
        return ('<InterfacialTension({0.n_m} N/m at {0.ref_temp_k}K, '
                'if={0.interface})>'
                .format(self))
