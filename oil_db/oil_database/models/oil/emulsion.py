#
# PyMODM model class for Environment Canada's emulsion
# oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import FloatField, CharField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin
from oil_database.models.common.float_unit import (FloatUnit,
                                                   TimeUnit,
                                                   TemperatureUnit,
                                                   AdhesionUnit,
                                                   DynamicViscosityUnit)


class Emulsion(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    water_content = EmbeddedDocumentField(FloatUnit)
    wc_standard_deviation = FloatField(blank=True)
    wc_replicates = FloatField(blank=True)

    age = EmbeddedDocumentField(TimeUnit)
    ref_temp = EmbeddedDocumentField(TemperatureUnit)
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    visual_stability = CharField(choices=('Entrained',
                                          'Did not form',
                                          'Unstable',
                                          'Stable',
                                          'Meso-stable'),
                                 blank=True)

    complex_modulus = EmbeddedDocumentField(AdhesionUnit, blank=True)
    cm_standard_deviation = FloatField(blank=True)

    storage_modulus = EmbeddedDocumentField(AdhesionUnit, blank=True)
    sm_standard_deviation = FloatField(blank=True)

    loss_modulus = EmbeddedDocumentField(AdhesionUnit, blank=True)
    lm_standard_deviation = FloatField(blank=True)

    tan_delta_v_e = FloatField(blank=True)
    td_standard_deviation = FloatField(blank=True)

    complex_viscosity = EmbeddedDocumentField(DynamicViscosityUnit,
                                              blank=True)
    cv_standard_deviation = FloatField(blank=True)

    mod_replicates = FloatField(blank=True)

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
        return ('<{}(water_content={}, temp={}, age={}, w={})>'
                .format(self.__class__.__name__,
                        self.water_content,
                        self.ref_temp, self.age, self.weathering))
