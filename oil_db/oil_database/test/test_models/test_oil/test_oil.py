"""
Tests of the data model class
"""
import json
from pathlib import Path

import pytest

from oil_database.models.oil import Oil, MetaData
from oil_database.models.oil.values import Reference


from pprint import pprint
# A few handy constants for use for tests

NAME = "A name for an oil"

# NOTE: this should be updated when the data model is updated.
BIG_RECORD = json.load(open(
    Path(__file__).parent / "AlaskaNorthSlope2015.json"
))


class TestOil:
    def test_init_empty(self):
        """ you must specify at least a name """
        with pytest.raises(TypeError):
            Oil()

    def test_empty_name(self):
        """ you must specify at least a name """
        with pytest.raises(TypeError):
            Oil(name="")

    def test_init_minimal(self):
        '''
            Even though we initialized with only a name, all attributes
            should be present.
        '''
        oil = Oil(name=NAME)
        assert oil.name == NAME

        for attr in ('name', 'oil_id', 'source_id',
                     'metadata', 'sub_samples', 'status', 'extra_data'):
            assert hasattr(oil, attr)

    def test_add_new_attribute(self):
        '''
            You should not be able to add an arbitrary new attribute
        '''
        oil = Oil(name=NAME)

        with pytest.raises(AttributeError):
            oil.random_attr = 456

    def test_json_minimal(self):
        '''
            When we convert our dataclass into a JSON struct, empty fields
            will be sparse.  The field will not be included in the struct.
            So if we create an Oil with only a name, it will look like this:

                {'name': 'A name for an oil'}
        '''
        oil = Oil(name=NAME)
        assert oil.name == NAME

        py_json = oil.py_json()

        assert py_json["name"] == NAME
        assert len(py_json) == 1  # only one item

    def test_json_minimal_nonsparse(self):
        oil = Oil(name=NAME)
        py_json = oil.py_json(sparse=False)

        pprint(py_json)

        assert len(py_json) == 8

        for attr in ['_id',
                     'oil_id',
                     'name',
                     'source_id',
                     'metadata',
                     'sub_samples',
                     'status',
                     'extra_data',
                     ]:
            assert attr in py_json

    def test_from_py_json_nothing(self):
        """
        you need to at least provide a name
        """
        py_json = {}
        with pytest.raises(TypeError):
            _oil = Oil.from_py_json(py_json)

    def test_from_py_json_minimal(self):
        '''
            Note: It seems we are not only checking for existence, but specific
                  values.  Parametrize??
        '''
        py_json = {"name": NAME}
        oil = Oil.from_py_json(py_json)

        assert oil.name == NAME
        assert oil.status == []
        assert oil.metadata.API is None

    def test_subsamples(self):
        """
        Is it getting all the subsamples
        """
        oil = Oil.from_py_json(BIG_RECORD)

        print("working with:", oil.name)

        assert len(oil.sub_samples) == 4
        assert oil.sub_samples[0].name == "Fresh Oil Sample"
        assert oil.sub_samples[3].name == "36.76% Weathered"


class TestMetaData:
    def test_init_empty(self):
        meta = MetaData()

        for attr in ('location',
                     'reference',
                     'sample_date',
                     'product_type',
                     'API',
                     'comments',
                     'labels'):
            assert hasattr(meta, attr)

    @pytest.mark.parametrize("attr, expected", (
        ('location', ''),
        ('reference', Reference(year=None, reference='')),
        ('sample_date', ''),
        ('product_type', ''),
        ('API', None),
        ('comments', ''),
        ('labels', []),
    ))
    def test_init_defaults(self, attr, expected):
        meta = MetaData()

        assert hasattr(meta, attr)
        assert getattr(meta, attr) == expected

    @pytest.mark.parametrize("attr, value, expected", (
        ('location', 'canada', 'canada'),
        ('reference',
         Reference(year=1999, reference='reference text'),
         Reference(year=1999, reference='reference text')),
        ('sample_date', '1999-01-01', '1999-01-01'),
        ('product_type', 'crude', 'crude'),
        ('API', 10.0, 10.0),
        ('comments', 'some comment', 'some comment'),
        ('labels', ['heavy'], ['heavy']),
    ))
    def test_init_set_attr(self, attr, value, expected):
        meta = MetaData()

        assert hasattr(meta, attr)

        setattr(meta, attr, value)
        assert getattr(meta, attr) == expected

    @pytest.mark.parametrize("attr, value, expected", (
        ('location', 'canada', {
            'default': '',
            'value': 'canada',
         }),
        ('reference', Reference(year=1999, reference='reference text'), {
            'default': Reference(year=None, reference=''),
            'value': Reference(year=1999, reference='reference text'),
         }),
        ('sample_date', '1999-01-01', {
            'default': '',
            'value': '1999-01-01',
         }),
        ('product_type', 'crude', {
            'default': '',
            'value': 'crude',
         }),
        ('API', 10.0, {
            'default': None,
            'value': 10.0,
            }
         ),
        ('comments', 'some comment', {
            'default': '',
            'value': 'some comment',
            }
         ),
        ('labels', ['heavy'], {
            'default': [],
            'value': ['heavy'],
            }
         ),
    ))
    def test_metadata_in_oil(self, attr, value, expected):
        oil = Oil(name=NAME)

        assert hasattr(oil.metadata, attr)
        assert getattr(oil.metadata, attr) == expected['default']

        setattr(oil.metadata, attr, value)
        assert getattr(oil.metadata, attr) == expected['value']
