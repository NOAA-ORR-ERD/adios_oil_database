'''
    class that represents the demographic data (metadata) of an oil record.
'''
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json
from ..common.measurement import MassFraction, Temperature

from .values import ProductType, Reference


@dataclass_to_json
@dataclass
class MetaData:
    name: str = ''
    source_id: str = ''
    location: str = ''
    reference: Reference = field(default_factory=Reference)
    sample_date: str = ''
    product_type: ProductType = ''
    API: float = None
    comments: str = ''
    labels: list = field(default_factory=list)
    model_completeness: float = None


@dataclass_to_json
@dataclass
class SampleMetaData:
    name: str = "Fresh Oil Sample"
    short_name: str = None
    sample_id: str = None
    fraction_weathered: MassFraction = None
    boiling_point_range: Temperature = None
