from adios_db.models.oil.location_info import validate_location

import pytest

def test_no_country():
    msgs = validate_location("No country, Here")

    assert not msgs

def test_country_right_order():
    msgs = validate_location("Alberta, Canada")

    assert not msgs

def test_two_word_country_right_order():
    msgs = validate_location("Busan, South Korea")

    assert not msgs

def test_country_wrong_order():
    msgs = validate_location("Canada, Alberta, something else")

    # ['W012: Location: "Canada, Alberta, something else" in wrong order. Should be: "Alberta, something else, Canada"']

    assert msgs[0].startswith('W012:')


def test_empty():
    msgs = validate_location("")

    assert not msgs
