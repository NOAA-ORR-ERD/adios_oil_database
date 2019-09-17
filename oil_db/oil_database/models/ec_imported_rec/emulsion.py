#
# PyMODM model class for Environment Canada's emulsion
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField, CharField


class ECEmulsion(EmbeddedMongoModel):
    water_content_percent = FloatField()
    wc_standard_deviation = FloatField(blank=True)
    wc_replicates = FloatField(blank=True)

    age_days = FloatField()
    ref_temp_c = FloatField()
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    visual_stability = CharField(choices=('Entrained',
                                          'Did not form',
                                          'Unstable',
                                          'Stable',
                                          'Meso-stable'),
                                 blank=True)

    complex_modulus_pa = FloatField(blank=True)
    cm_standard_deviation = FloatField(blank=True)

    storage_modulus_pa = FloatField(blank=True)
    sm_standard_deviation = FloatField(blank=True)

    loss_modulus_pa = FloatField(blank=True)
    lm_standard_deviation = FloatField(blank=True)

    tan_delta_v_e = FloatField(blank=True)
    td_standard_deviation = FloatField(blank=True)

    complex_viscosity_pa_s = FloatField(blank=True)
    cv_standard_deviation = FloatField(blank=True)

    mod_replicates = FloatField(blank=True)

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

        super(ECEmulsion, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{}(water_percent={}, temp={}C, age={} days, w={})>'
                .format(self.__class__.__name__,
                        self.water_content_percent,
                        self.ref_temp_c, self.age_days, self.weathering))
