"""
testing the oil model with a large, full, record
"""
import json
from pathlib import Path
import pytest

from oil_database.models.oil.oil import Oil


# NOTE: this should be updated when the data model is updated.
BIG_RECORD = json.load(open(Path(__file__).parent / "AlaskaNorthSlope2015.json"))


def test_subsamples():
    """
    Is it getting all the subsamples
    """
    oil = Oil.from_py_json(BIG_RECORD)

    print("working with:", oil.name)

    assert len(oil.sub_samples) == 4
    assert oil.sub_samples[0].name == "Fresh Oil Sample"
    assert oil.sub_samples[3].name == "36.76% Weathered"
