#
# PyMODM model class for benzene oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import FloatField, CharField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin

# we are probably not talking about concentrations of benzene in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Benzene(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    benzene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    toluene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    ethylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    m_p_xylene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    o_xylene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    isopropylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                             blank=True)
    propylebenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                           blank=True)
    isobutylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                            blank=True)
    amylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    n_hexylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                           blank=True)

    _1_2_3_trimethylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                    blank=True)
    _1_2_4_trimethylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                    blank=True)
    _1_2_dimethyl_4_ethylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                         blank=True)
    _1_3_5_trimethylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                    blank=True)
    _1_methyl_2_isopropylbenzene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                         blank=True)
    _2_ethyltoluene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                            blank=True)
    _3_4_ethyltoluene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                              blank=True)

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
        return ('<{}(benzene={}, w={})>'
                .format(self.__class__.__name__,
                        self.benzene, self.weathering))
