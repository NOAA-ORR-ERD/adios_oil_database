"""
Class that represents the demographic data (metadata) of an oil record.
"""
from datetime import datetime
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import MassFraction, Temperature

from .values import Reference
from .product_type import ProductType, DOESNT_NEED_API
from .location_coordinates import LocationCoordinates

from .validation.warnings import WARNINGS
from .validation.errors import ERRORS


@dataclass_to_json
@dataclass
class ChangeLogEntry:
    name: str = ""
    date: str = ""
    comment: str = ""

    def validate(self):
        msgs = []

        # check date is valid
        if self.date:
            try:
                datetime.fromisoformat(self.date)
            except ValueError as err:
                msgs.append(WARNINGS["W011"]
                            .format("change log entry", self.date, str(err)))

        return msgs


class ChangeLog(JSON_List):
    item_type = ChangeLogEntry


@dataclass_to_json
@dataclass
class MetaData:
    name: str = ''
    source_id: str = ''
    alternate_names: list = field(default_factory=list)
    location: str = ''
    reference: Reference = field(default_factory=Reference)
    sample_date: str = ''
    product_type: ProductType = ''
    API: float = None
    comments: str = ''
    labels: list = field(default_factory=list)
    model_completeness: float = None
    location_coordinates: LocationCoordinates = None
    gnome_suitable: bool = None
    change_log: ChangeLog = field(default_factory=ChangeLog)

    def __post_init__(self):
        """
        force API to be a float
        """
        if self.API is not None:
            self.API = float(self.API)


    def validate(self):
        msgs = []

        # check for API
        api = self.API
        if api is None:
            if self.product_type in DOESNT_NEED_API:
                pass
                # disabled this -- it was annoying
                # msgs.append(WARNINGS["W004"])
            else:
                msgs.append(ERRORS["E030"])
        else:
            if not (-60.0 < api < 100):  # somewhat arbitrary limits
                msgs.append(WARNINGS["W005"].format(api=api))

        # Check for a reasonable name
        # right now, reasonable is more than 5 characters -- we may want to add
        # more later
        if len(self.name.strip()) < 2:
            msgs.append(WARNINGS["W001"].format(self.name))

        # check sample date is valid
        if self.sample_date:
            try:
                datetime.fromisoformat(self.sample_date)
            except ValueError as err:
                msgs.append(WARNINGS["W011"]
                            .format("sample date", self.sample_date, str(err)))

        return msgs


@dataclass_to_json
@dataclass
class SampleMetaData:
    name: str = "Fresh Oil Sample"
    short_name: str = None
    sample_id: str = None
    description: str = None
    fraction_evaporated: MassFraction = None
    boiling_point_range: Temperature = None
