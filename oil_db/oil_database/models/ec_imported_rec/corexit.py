#
# PyMODM model class for Environment Canada's emulsion
# oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import FloatField

from oil_database.models.common.float_unit import FloatUnit


class ECCorexit9500(EmbeddedMongoModel):
    '''
        Chemical dispersability with Corexit 9500 Dispersant (swirling flask
        test) (ASTM F2059)
    '''
    dispersant_effectiveness = EmbeddedDocumentField(FloatUnit, blank=True)
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

        super(ECCorexit9500, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{}(effectiveness={}%, w={})>'
                .format(self.__class__.__name__,
                        self.dispersant_effectiveness, self.weathering))
