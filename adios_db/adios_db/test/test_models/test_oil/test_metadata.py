"""
tests for the metadata objects


not much here -- for the most part they are tested as parts of teh Oil
"""

from adios_db.models.oil.metadata import MetaData

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



