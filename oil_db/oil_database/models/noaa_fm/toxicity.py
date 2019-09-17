#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class NoaaFmToxicity(EmbeddedMongoModel):
    tox_type = CharField(choices=('EC', 'LC'))
    species = CharField(max_length=24)
    after_24h = FloatField(blank=True)
    after_48h = FloatField(blank=True)
    after_96h = FloatField(blank=True)

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(NoaaFmToxicity, self).__init__(**kwargs)

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                '{0.species}, {0.tox_type}, '
                '[{0.after_24h}, {0.after_48h}, {0.after_96h}])>'
                .format(self))
