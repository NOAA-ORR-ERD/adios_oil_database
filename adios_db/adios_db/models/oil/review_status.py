"""
simple class to hold the review status of a record
"""
from datetime import datetime
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json

from ..common.validators import EnumValidator, DateTimeValidator

from .validation.errors import ERRORS
from .validation.warnings import WARNINGS


@dataclass_to_json
@dataclass
class ReviewStatus:
    status: str = "Not Reviewed"
    reviewers: str = ""
    review_date: str = ""
    notes: str = ""

    _status_validator = EnumValidator(["Not Reviewed",
                                       "Under Review",
                                       "Review Complete"],
                                      ERRORS['E013'],
                                      case_insensitive=True)

    def validate(self):
        msgs = []

        # keep two formatting place holders
        date_validator = DateTimeValidator(err_msg = WARNINGS["W011"].format("review date","{}","{}"))

        if self.review_date:
            msgs.extend(date_validator(self.review_date))

        msgs.extend(self._status_validator(self.status))

        return msgs
