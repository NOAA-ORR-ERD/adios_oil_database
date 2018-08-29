#
# PyMODM model class for Environment Canada's emulsion
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField, CharField


class Emulsion(EmbeddedMongoModel):
    water_content_fraction = FloatField()
    age_days = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    # may as well keep the extra stuff
    standard_deviation = FloatField(blank=True)
    replicates = FloatField(blank=True)
    complex_viscosity_pa_s = FloatField(blank=True)
    complex_modulus_pa = FloatField(blank=True)
    loss_modulus_pa = FloatField(blank=True)
    storage_modulus_pa = FloatField(blank=True)
    tan_delta_v_e = FloatField(blank=True)
    visual_stability = CharField(choices=('Entrained',
                                          'Did not form',
                                          'Unstable',
                                          'Stable',
                                          'Meso-stable'),
                                 blank=True)

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

        super(Emulsion, self).__init__(**kwargs)

    def __repr__(self):
        return ('<Emulsion('
                'complex_mod={0.complex_modulus_pa:0.3g} Pa, '
                'storage_mod={0.storage_modulus_pa:0.3g} Pa, '
                'loss_mod={0.loss_modulus_pa:0.3g} Pa, '
                'tan_delta={0.tan_delta_v_e:0.3g} V/E, '
                'complex_vis={0.complex_viscosity_pa_s:0.3g} Pa.s, '
                'water_content={0.water_content_fraction:0.3g}, '
                'temp={0.ref_temp_k}K, '
                'age={0.age_days} days, '
                'weathering={0.weathering})>'
                .format(self))
