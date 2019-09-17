#
# PyMODM Model class definitions for our category object
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (CharField, ReferenceField, ListField)


class Category(MongoModel):
    '''
        This is a self referential object suitable for building a
        hierarchy of nodes.  The relationship will be one-to-many
        child nodes.
        So Categories will be a tree of terms that the user can use to
        narrow down the list of oils he/she is interested in.
        We will support the notion that an oil can have many categories,
        and a category can contain many oils.
        Thus, Oil objects will be linked to categories in a many-to-many
        relationship.
    '''
    name = CharField(max_length=80, required=True)

    parent = ReferenceField('Category')

    children = ListField(ReferenceField('Category'), blank=True, default=[])

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'oil-db-app'
        indexes = [IndexModel([('name', ASCENDING)], unique=False)]

    def __init__(self, **kwargs):
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(Category, self).__init__(**kwargs)

        # Annoying: ListField() doesn't handle container default args
        self.children = []

    def append(self, child):
        child.parent = self
        child.save()

        self.children.append(child)

        return self

    def __repr__(self):
        return ('<Category({}, parent={})>'
                .format(self.name,
                        self.parent.name if self.parent is not None else None))

    def __str__(self):
        return self.__repr__()
