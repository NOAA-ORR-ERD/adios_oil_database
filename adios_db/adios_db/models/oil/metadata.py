"""
Class that represents the demographic data (metadata) of an oil record.
"""
from datetime import datetime
from dataclasses import dataclass, field

from ...util import sigfigs
from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import MassFraction, Temperature

from .values import Reference
from .product_type import ProductType, DOESNT_NEED_API
from .location_coordinates import LocationCoordinates
from .location_info import validate_location

from .validation.warnings import WARNINGS
from .validation.errors import ERRORS
from .validation import is_not_iso_or_year
from ..common.validators import DateTimeValidator

@dataclass_to_json
@dataclass
class ChangeLogEntry:
    name: str = ""
    date: str = ""
    comment: str = ""

    def validate(self):
        # keep two formatting place holders
        date_validator = DateTimeValidator(err_msg = WARNINGS["W011"].format("change log entry","{}","{}"))

        if self.date:
            msgs = date_validator(self.date)

        # if self.date:
        #     try:
        #         datetime.fromisoformat(self.date)
        #     except ValueError as err:
        #         msgs.append(WARNINGS["W011"].format(
        #             "change log entry", self.date, str(err)
        #         ))

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
        Assorted cleanup
        """
        # force API to be a float if possible, otherwise set it to None.
        # also reduce the number of sigfigs
        if self.API is not None:
            try:
                self.API = sigfigs(float(self.API), 4)
            except ValueError:
                self.API = None

        # make sure lists are sorted
        self.labels = sorted(self.labels)
        self.alternate_names = sorted(self.alternate_names)
        # normalize case of product type
        self.product_type = ProductType.normalize_product_type(self.product_type)

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
        sd = self.sample_date
        if sd:
            err = is_not_iso_or_year(sd)
            if err:
                msgs.append(WARNINGS["W011"].format("sample date", self.sample_date, str(err)))
        # validate the location:
        msgs.extend(validate_location(self.location))

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
