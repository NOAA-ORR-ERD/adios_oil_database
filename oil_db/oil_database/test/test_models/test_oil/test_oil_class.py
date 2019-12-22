"""
Tests of the data model class
"""

import pytest
import dataclasses
from pprint import pprint

from oil_database.models.oil.oil_class import Oil

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


def test_json_just_name():
    oil = Oil(name=NAME)
    assert oil.name == NAME

    py_json = oil.py_json()
    assert py_json == {"name": NAME}


def test_json_a_few_fields():
    oil = Oil(name=NAME,
              api=32.5,
              product_type="Crude",
              labels=["medium crude", "sweet crude"],
              )
    py_json = oil.py_json()
    assert py_json == {'name': NAME,
                       'api': 32.5,
                       'product_type':
                       'Crude',
                       'labels': ['medium crude', 'sweet crude']
                       }


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



def test_pyson():
    oil = Oil(name=NAME)

#    py_json = oil.py_json(sparse=False)
    py_json = oil.py_json(sparse=True)

    pprint(py_json)

    assert False


# def test_fields():
#     oil = Oil(name=NAME)

#     print(dataclasses.fields(oil))

#     assert False



