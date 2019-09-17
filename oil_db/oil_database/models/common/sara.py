#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class SARAFraction(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    fraction = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    standard_deviation = FloatField(blank=True)
    replicates = FloatField(blank=True)
    method = CharField(max_length=16, blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        # Seriously?  What good is a default if it can't negotiate None values?
        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        if 'ref_temp_k' not in kwargs or kwargs['ref_temp_k'] is None:
            kwargs['ref_temp_k'] = 273.15

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<SARAFraction({0.sara_type}={0.fraction} '
                'at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))


class SARADensity(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super().__init__(**kwargs)

    def __repr__(self):
        return ('<SARADensity('
                '{0.sara_type}={0.kg_m_3} kg/m^3 at {0.ref_temp_k}K)>'
                .format(self))


class MolecularWeight(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    g_mol = FloatField()
    ref_temp_k = FloatField()

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super().__init__(**kwargs)

    @property
    def kg_mol(self):
        return self.g_mol / 1000.0

    @kg_mol.setter
    def length(self, value):
        self.g_mol = value * 1000.0

    def __repr__(self):
        return ('<MolecularWeight('
                '{0.sara_type}={0.g_mol} gm/mol at {0.ref_temp_k}K)>'
                .format(self))
