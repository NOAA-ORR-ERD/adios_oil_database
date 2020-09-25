from dataclasses import dataclass
from ..common.utilities import dataclass_to_json


@dataclass_to_json
@dataclass
class Label:
    '''
        So Labels will be a collection terms that the user can use to
        narrow down the list of oils he/she is interested in.
    '''
    name: str
