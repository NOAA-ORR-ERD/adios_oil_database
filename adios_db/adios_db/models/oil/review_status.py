"""
simple class to hold the review status of a record
"""

from ..common.validation import EnumValidator


@dataclass_to_json
@dataclass
class ReviewStatus:
    status: str = "not reviewed"
    reviewers: str = ""
    review_date: str = ""
    notes: str = ""

    validate = EnumValidator(["Not Reviewed", "Under Review", "Review Complete"])


