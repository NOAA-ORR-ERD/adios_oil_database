#
# PyMODM model class for Environment Canada's n-Alkane
# oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class NAlkanes(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    '''
        n-Alkanes (ug/g oil) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    pristane = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    phytane = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c8 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c9 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c10 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c11 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c12 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c13 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c14 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c15 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c16 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c17 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c18 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c19 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c20 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c21 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c22 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c23 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c24 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c25 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c26 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c27 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c28 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c29 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c30 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c31 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c32 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c33 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c34 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c35 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c36 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c37 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c38 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c39 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c40 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c41 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c42 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c43 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c44 = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        self._set_embedded_property_args(kwargs)

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'pristane={0.pristane}, '
                'phytane={0.phytane}, '
                'c8={0.c8}, '
                'c9={0.c9}, '
                'c10={0.c10}, '
                'c11={0.c11}, '
                'c12={0.c12}, '
                'c13={0.c13}, '
                'c14={0.c14}, '
                'c15={0.c15}, '
                'c16={0.c16}, '
                'c17={0.c17}, '
                'c18={0.c18}, '
                'c19={0.c19}, '
                'c20={0.c20}, '
                'c21={0.c21}, '
                'c22={0.c22}, '
                'c23={0.c23}, '
                'c24={0.c24}, '
                'c25={0.c25}, '
                'c26={0.c26}, '
                'c27={0.c27}, '
                'c28={0.c28}, '
                'c29={0.c29}, '
                'c30={0.c30}, '
                'c31={0.c31}, '
                'c32={0.c32}, '
                'c33={0.c33}, '
                'c34={0.c34}, '
                'c35={0.c35}, '
                'c36={0.c36}, '
                'c37={0.c37}, '
                'c38={0.c38}, '
                'c39={0.c39}, '
                'c40={0.c40}, '
                'c41={0.c41}, '
                'c42={0.c42}, '
                'c43={0.c43}, '
                'c44={0.c44}, '
                'weathering={0.weathering})>'
                .format(self))
