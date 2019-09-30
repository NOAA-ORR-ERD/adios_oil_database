#
# Model class definitions for our category object
#
from typing import List

from .base_model import PydObjectId, MongoBaseModel


class Category(MongoBaseModel):
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
    _id: PydObjectId = None
    name: str
    parent: PydObjectId = None
    children: List[PydObjectId] = []

    def append(self, child):
        child.parent = self._id
        self.children.append(child._id)

        child.save()
        self.save()

        return self


Category.update_forward_refs()  # this is to support the self-reference
