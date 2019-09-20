#
# Model class definitions for our category object
#
from pydantic import BaseModel
from typing import Type, List


class Category(BaseModel):
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
    name: str
    parent: 'Category'
    children: List['Category'] = []

    def append(self, child):
        child.parent = self
        self.children.append(child)

        return self


Category.update_forward_refs()  # this is to support the self-reference
