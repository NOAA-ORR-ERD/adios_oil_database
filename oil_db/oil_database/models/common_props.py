#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class Synonym(EmbeddedMongoModel):
    name = CharField(max_length=40)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(Synonym, self).__init__(**kwargs)

    def __repr__(self):
        return "<Synonym('%s')>" % (self.name)


class Density(EmbeddedMongoModel):
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

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

        super(Density, self).__init__(**kwargs)

    def __repr__(self):
        return ("<Density({0.kg_m_3} kg/m^3 at {0.ref_temp_k}K)>"
                .format(self))


class KVis(EmbeddedMongoModel):
    m_2_s = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(KVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<KVis({0.m_2_s} m^2/s at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))


class DVis(EmbeddedMongoModel):
    kg_ms = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(DVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<DVis({0.kg_ms} kg/ms at {0.ref_temp_k}K, w={0.weathering})>'
                .format(self))


class Cut(EmbeddedMongoModel):
    vapor_temp_k = FloatField(blank=True)
    liquid_temp_k = FloatField(blank=True)
    fraction = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(Cut, self).__init__(**kwargs)

    def __repr__(self):
        lt = '{0}K'.format(self.liquid_temp_k) if self.liquid_temp_k else None
        vt = '{0}K'.format(self.vapor_temp_k) if self.vapor_temp_k else None
        return ('<Cut(liquid_temp={0}, vapor_temp={1}, fraction={2})>'
                .format(lt, vt, self.fraction))


class Toxicity(EmbeddedMongoModel):
    tox_type = CharField(choices=('EC', 'LC'))
    species = CharField(max_length=24)
    after_24h = FloatField(blank=True)
    after_48h = FloatField(blank=True)
    after_96h = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(Toxicity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<Toxicity({0.species}, {0.tox_type}, '
                '[{0.after_24h}, {0.after_48h}, {0.after_96h}])>'
                .format(self))


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

        super(SARAFraction, self).__init__(**kwargs)

    def __repr__(self):
        return ('<SARAFraction({0.sara_type}={0.fraction} at {0.ref_temp_k}K)>'
                .format(self))


class SARADensity(EmbeddedMongoModel):
    sara_type = CharField(choices=('Saturates', 'Aromatics',
                                   'Resins', 'Asphaltenes'))
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(SARADensity, self).__init__(**kwargs)

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

        super(MolecularWeight, self).__init__(**kwargs)

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
