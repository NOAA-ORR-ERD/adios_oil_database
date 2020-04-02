"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from .values import ProductType
from .sample import Sample, SampleList

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass_to_json
@dataclass
class Oil:
    # metadata:
    name: str  # only required field
    _id: str = ""
    oil_id: str = ""

    location: str = ""
    reference: str = ""
    sample_date: str = ""
    comments: str = ""
    API: float = None
    product_type: ProductType = ""

    labels: list = field(default_factory=list)
    status: list = field(default_factory=list)
    extra_data: dict = field(default_factory=dict)

    sub_samples: SampleList = field(default_factory=SampleList)

    def __post_init__(self):
        """
        put any validation code here (__init__ is auto-generated by dataclass)

        right now, a non-empty name is it.
        """
        if self.name == "":
            raise TypeError("Name must be a non-empty string")
