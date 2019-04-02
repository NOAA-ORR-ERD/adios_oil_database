from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import (CharField,
                           FloatField)

from oil_database.models.common.float_unit import (TemperatureUnit,
                                                   InterfacialTensionUnit)


class InterfacialTension(EmbeddedMongoModel):
    '''
        TODO: The unit conversion package doesn't have any unit conversions
              for interfacial tension.  We will continue to use a float field
              for now, but we need to add an InterfacialTensionUnit type soon.
    '''
    tension = EmbeddedDocumentField(InterfacialTensionUnit)
    ref_temp = EmbeddedDocumentField(TemperatureUnit)
    interface = CharField(choices=('air', 'water', 'seawater'))
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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.tension} at {0.ref_temp}, '
                'if={0.interface}, w={0.weathering})>'
                .format(self))
