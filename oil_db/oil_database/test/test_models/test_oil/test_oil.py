"""
Tests of the data model class
"""

import pytest
from pprint import pprint

from oil_database.models.oil.oil import Oil

# A few handy constants for use for tests

NAME = "A name for an oil"




def test_minimal():
    oil = Oil(name=NAME)
    assert oil.name == NAME


def test_noname():
    """ you must specify at least a name """
    with pytest.raises(TypeError):
        oil = Oil()


def test_empty_string_name():
    """ you must specify at least a name """
    with pytest.raises(TypeError):
        oil = Oil(name="")


# @pytest.mark.xfail
def test_json_just_name():
    """
    This is essentially the very minimal record

    It will look like this:

    {'name': 'A name for an oil',
     'samples': [{'name': 'Fresh, Unweathered Oil', 'short_name': 'Fresh'}]}
    """
    oil = Oil(name=NAME)
    assert oil.name == NAME

    py_json = oil.py_json()

    pprint(py_json)

    assert py_json["name"] == NAME
    assert len(py_json) == 2  # only two items
    assert 'samples' in py_json


def test_json_a_few_fields():
    oil = Oil(name=NAME,
              api=32.5,
              labels=["medium crude", "sweet crude"],
              )
    oil.product_type="Crude"
    py_json = oil.py_json()

    assert len(py_json) == 5
    assert py_json["name"] == NAME
    assert py_json["api"] == 32.5
    assert py_json["labels"] == ["medium crude", "sweet crude"]
    assert py_json["product_type"] == "Crude"
    assert 'samples' in py_json


def test_json_nonsparse():
    oil = Oil(name=NAME)

    py_json = oil.py_json(sparse=False)

    print(py_json)

    for key in ['name',
                'oil_id',
                'location',
                'reference',
                'reference_date',
                'sample_date',
                'comments',
                'api',
                'product_type',
                'labels',
                'status',
                ]:
        assert key in py_json

def test_add_new_attribute():
    """
    you should not be able to add an aarbitrary new attribute
    """
    oil = Oil(name=NAME)

    with pytest.raises(AttributeError):
        oil.random_attr = 456


def test_pyson():
    oil = Oil(name=NAME)

#    py_json = oil.py_json(sparse=False)
    py_json = oil.py_json(sparse=True)

    pprint(py_json)


# def test_fields():
#     oil = Oil(name=NAME)

#     print(dataclasses.fields(oil))

#     assert False


