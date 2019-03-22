#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class NoaaFmDensity(EmbeddedMongoModel):
    kg_m_3 = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

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

        super(NoaaFmDensity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmDensity({0.kg_m_3} kg/m^3 at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))


class NoaaFmKVis(EmbeddedMongoModel):
    m_2_s = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(NoaaFmKVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmKVis({0.m_2_s} m^2/s at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))


class NoaaFmDVis(EmbeddedMongoModel):
    kg_ms = FloatField()
    ref_temp_k = FloatField()
    weathering = FloatField(default=0.0)

    method = CharField(max_length=20, blank=True)
    replicates = FloatField(blank=True)
    standard_deviation = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            kwargs['weathering'] = 0.0

        super(NoaaFmDVis, self).__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmDVis({0.kg_ms} kg/ms at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))


class NoaaFmCut(EmbeddedMongoModel):
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

        super(NoaaFmCut, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        lt = '{}K'.format(self.liquid_temp_k) if self.liquid_temp_k else None
        vt = '{}K'.format(self.vapor_temp_k) if self.vapor_temp_k else None
        return ('<NoaaFmCut(liquid_temp={}, vapor_temp={}, fraction={}, w={})>'
                .format(lt, vt, self.fraction, self.weathering))


class NoaaFmToxicity(EmbeddedMongoModel):
    tox_type = CharField(choices=('EC', 'LC'))
    species = CharField(max_length=24)
    after_24h = FloatField(blank=True)
    after_48h = FloatField(blank=True)
    after_96h = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(NoaaFmToxicity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<NoaaFmToxicity({0.species}, {0.tox_type}, '
                '[{0.after_24h}, {0.after_48h}, {0.after_96h}])>'
                .format(self))
