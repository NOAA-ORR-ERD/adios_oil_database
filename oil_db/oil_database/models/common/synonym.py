#
# PyMODM Model class definitions for embedded content in our oil records
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField


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
