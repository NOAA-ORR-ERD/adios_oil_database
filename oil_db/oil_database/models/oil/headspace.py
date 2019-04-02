#
# PyMODM model class for headspace oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Headspace(EmbeddedMongoModel):
    '''
        Headspace Analysis (mg/g oil) (ESTS 2002b)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    n_c5 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    n_c6 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    n_c7 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    n_c8 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    c5_group = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c6_group = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c7_group = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

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

        super(Headspace, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'n_c5={0.n_c5}, '
                'n_c6={0.n_c6}, '
                'n_c7={0.n_c7}, '
                'n_c8={0.n_c8}, '
                'c5_group={0.c5_group}, '
                'c6_group={0.c6_group}, '
                'c7_group={0.c7_group}, '
                'w={0.weathering})>'
                .format(self))
