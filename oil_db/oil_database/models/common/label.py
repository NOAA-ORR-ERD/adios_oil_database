#
# Model class definitions for our label(category) object
#
from .base_model import PydObjectId, MongoBaseModel


class Label(MongoBaseModel):
    '''
        So Labels will be a collection terms that the user can use to
        narrow down the list of oils he/she is interested in.
    '''
    _id: PydObjectId = None
    name: str
