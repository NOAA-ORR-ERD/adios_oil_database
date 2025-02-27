"""
tests for the metadata objects

not much here -- for the most part they are tested as parts of the Oil
"""
from pathlib import Path
import json

from adios_db.models.oil.metadata import MetaData, ChangeLogEntry, ChangeLog
from adios_db.models.oil.oil import Oil

# this really should be somewhere more central
from .test_validation.test_validation import (snippet_in_oil_status,
                                              snippet_not_in_oil_status)


EXAMPLE_DATA_DIR = (Path(__file__).parent.parent.parent
                    / "data_for_testing"
                    / "example_data")
full_oil_filename = EXAMPLE_DATA_DIR / "ExampleFullRecord.json"

MD_JSON = """
{
"name": "Access West Blend Winter",
"source_id": "2234",
"location": "Alberta, Canada",
"reference": {
    "year": 2020,
    "reference": "Personal communication from Fatemeh Mirnaghi (ESTS), date: April 21, 2020."
},
"sample_date": "2013-04-08",
"product_type": "Bitumen Blend",
"API": 20.93,
"comments": "Via CanmetEnergy, Natural Resources Canada",
"labels": [
    "Crude Oil",
    "Heavy Crude"
],
"model_completeness": 94,
"change_log": [
    {
        "name": "Bozo the Clown",
        "date": "2021-04-01",
        "comment": "Any random old thing"
    }
]
}
"""


def test_metadata_from_json():
    """
    see if we can make one from JSON

    fixme: there could be a lot more checks here, but ...
    """
    md = MetaData.from_py_json(json.loads(MD_JSON))

    assert md.sample_date == "2013-04-08"
    assert md.product_type == "Bitumen Blend"


def test_metadata_from_full_record():
    oil = Oil.from_file(full_oil_filename)
    log = oil.metadata.change_log

    print(log)
    assert len(log) == 1
    assert log[0].name == "Bozo the Clown"
    assert log[0].date == "2021-04-01"
    assert log[0].comment == "Any random old thing"


def test_good_sample_date():
    md = MetaData(sample_date="1965-10-20")
    msgs = md.validate()

    print(msgs)
    assert snippet_not_in_oil_status("W011", msgs)


def test_no_sample_date():
    md = MetaData()
    msgs = md.validate()

    print(msgs)
    assert snippet_not_in_oil_status("W011", msgs)


def test_bad_sample_date():
    md = MetaData(sample_date="1965-20-10")
    msgs = md.validate()

    print(msgs)
    assert snippet_in_oil_status("W011", msgs)


def test_missing_API_crude():
    md = MetaData()
    md.product_type = "Crude Oil NOS"
    msgs = md.validate()

    print(msgs)
    assert snippet_in_oil_status("E030", msgs)


def test_missing_API_solvent():
    md = MetaData()
    md.product_type = "Solvent"
    msgs = md.validate()

    print(msgs)
    assert snippet_not_in_oil_status("E030", msgs)
    # turned this off
    assert snippet_not_in_oil_status("W004", msgs)


def test_API_always_float():
    """
    the API should get converte to a float if it's an integer in the JSON, etc.
    """
    md = MetaData(API=32)

    assert type(md.API) == float


#
# ChangeLogEntry tests
#
def test_ChangeLogEntry_init():
    cle = ChangeLogEntry(name="Bozo the Clown",
                         date="2021-04-01",
                         comment="Any random old thing")

    assert cle.name == "Bozo the Clown"
    assert cle.date == "2021-04-01"
    assert cle.comment == "Any random old thing"


def test_ChangeLogEntry_date_valid():
    cle = ChangeLogEntry(name="Bozo the Clown",
                         date="2021-04-01",
                         comment="Any random old thing")

    msgs = cle.validate()

    assert not msgs


def test_ChangeLogEntry_date_not_alid():
    cle = ChangeLogEntry(name="Bozo the Clown",
                         date="2021-040-01",
                         comment="Any random old thing")

    msgs = cle.validate()

    assert msgs == ["W011: change log entry date format: 2021-040-01 "
                    "is invalid: Invalid isoformat string: '2021-040-01'"]


def test_ChangeLog():
    cl = ChangeLog()
    cl.append(ChangeLogEntry(
        name="Bozo the Clown",
        date="2021-040-01",
        comment="Any random old thing",
    ))

    cl.append(ChangeLogEntry(
        name="Frumpy the Clown",
        date="2021-04-01",
        comment="Some more stupid data",
    ))

    pjs = cl.py_json()
    cl2 = ChangeLog.from_py_json(pjs)

    assert cl == cl2

    msgs = cl.validate()

    print(msgs)
    assert msgs == ["W011: change log entry date format: 2021-040-01 "
                    "is invalid: Invalid isoformat string: '2021-040-01'"]

def test_bad_log_date():
    md = MetaData()
    md.change_log.append(ChangeLogEntry(
        name="Bozo the Clown",
        date="2021-040-01",
        comment="Any random old thing",
    ))

    msgs = md.validate()

    print(msgs)
    print(md.py_json())
    assert snippet_in_oil_status("W011", msgs)

def test_normalize_product_type():
    md = MetaData(product_type="crude  oil NOS")

    assert md.product_type == "Crude Oil NOS"

def test_sigfigs_in_API():
    md = MetaData(API="32.123456789")

    assert md.API == 32.12

def test_location_validation():
    md = MetaData(location="Canada, Alberta")

    msgs = md.validate()

    for msg in msgs:
        if "W012" in msg:
            there = True
            break
        else:
            there = False

    assert there

