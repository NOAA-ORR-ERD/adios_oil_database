#
# PyMODM model class for Environment Canada's interfacial tension
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import (CharField,
                           FloatField)


class ECInterfacialTension(EmbeddedMongoModel):
    dynes_cm = FloatField()
    ref_temp_c = FloatField()
    interface = CharField(choices=('air', 'water', 'seawater'))
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    method = CharField(max_length=32, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
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
        return ('<ECInterfacialTension({0.dynes_cm} dynes/cm '
                'at {0.ref_temp_c}C, '
                'if={0.interface}, w={0.weathering})>'
                .format(self))
