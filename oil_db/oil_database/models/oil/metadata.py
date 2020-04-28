'''
    class that represents the demographic data (metadata) of an oil record.
'''
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json

from .values import ProductType, Reference


@dataclass_to_json
@dataclass
class MetaData:
    location: str = ""
    reference: Reference = field(default_factory=Reference)
    sample_date: str = ""
    product_type: ProductType = ""
    API: float = None
    comments: str = ""
    labels: list = field(default_factory=list)
