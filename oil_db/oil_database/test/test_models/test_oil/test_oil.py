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


@pytest.mark.xfail
def test_json_just_name():
    oil = Oil(name=NAME)
    assert oil.name == NAME

    py_json = oil.py_json()
    assert py_json == {"name": NAME}


@pytest.mark.xfail
def test_json_a_few_fields():
    oil = Oil(name=NAME,
              api=32.5,
              labels=["medium crude", "sweet crude"],
              )
    oil.product_type="Crude"
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


