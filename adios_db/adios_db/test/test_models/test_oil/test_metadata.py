"""
tests for the metadata objects


not much here -- for the most part they are tested as parts of the Oil
"""

from adios_db.models.oil.metadata import MetaData, ChangeLogEntry, ChangeLog

# this really should be somewhere more central
from adios_db.test.test_models.test_oil.test_validation.test_validation \
    import (snippet_in_oil_status,
            snippet_not_in_oil_status,
            )


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

# ######
# ChangeLogEntry tests
def test_ChangeLogEntry_init():
    cle = ChangeLogEntry(name="Bozo the Clown",
                         date="2021-04-01",
                         comment="Any random old thing",
                         )

    assert cle.name == "Bozo the Clown"
    assert cle.date == "2021-04-01"
    assert cle.comment == "Any random old thing"


def test_ChangeLogEntry_date_valid():
    cle = ChangeLogEntry(name="Bozo the Clown",
                         date="2021-04-01",
                         comment="Any random old thing",
                         )

    msgs = cle.validate()

    assert not msgs


def test_ChangeLogEntry_date_not_alid():
    cle = ChangeLogEntry(name="Bozo the Clown",
                         date="2021-040-01",
                         comment="Any random old thing",
                         )

    msgs = cle.validate()

    assert msgs == ["W011: change log entry date format: 2021-040-01 "
                    "is invalid: Invalid isoformat string: '2021-040-01'"]


def test_ChangeLog():
    cl = ChangeLog()
    cl.append(ChangeLogEntry(name="Bozo the Clown",
                             date="2021-040-01",
                             comment="Any random old thing",
                             ))

    cl.append(ChangeLogEntry(name="Frumpy the Clown",
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
    md.change_log.append(ChangeLogEntry(name="Bozo the Clown",
                                        date="2021-040-01",
                                        comment="Any random old thing",
                                        ))

    msgs = md.validate()

    print(msgs)

    assert snippet_in_oil_status("W011", msgs)
