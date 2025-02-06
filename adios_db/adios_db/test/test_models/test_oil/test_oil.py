"""
Tests of the data model class
"""
import json
from pathlib import Path

import pytest

from adios_db.models.oil.oil import Oil, ADIOS_DATA_MODEL_VERSION
from adios_db.models.oil.version import VersionError
from adios_db.models.oil.metadata import MetaData
from adios_db.models.oil.values import Reference

from pprint import pprint


# A few handy constants for use for tests
OIL_ID = 'AD00123'

HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"
TEST_DATA_DIR = (HERE.parent.parent
                 / "data_for_testing" / "noaa-oil-data" / "oil")
EXAMPLE_DATA_DIR = HERE.parent.parent / "data_for_testing" / "example_data"

BIG_RECORD = json.load(open(TEST_DATA_DIR / "EC" / "EC02234.json",
                            encoding="utf-8"))


class TestOil:
    def test_init_empty(self):
        """
        You must specify at least an oil_id
        """
        with pytest.raises(TypeError):
            Oil()

    def test_wrong_thing_in_oil_id(self):
        """
        it's easy to accidentally pass who knows what into the id param

        that should get flagged if it doesn't make sense
        """
        whoops = {'oil_id': 'AD00123', 'metadata': {'name': 'An oil name'}}
        with pytest.raises(ValueError):
            # error because we're passing the whole dict in
            Oil(whoops)

    def test_bad_oil_id(self):
        """
        it's easy to accidentally pass who knows what into the id param

        a really long string probably isn't what you meant
        """
        whoops = {
            'oil_id': 'AD00123',
            'metadata': {
                'name': 'An oil name',
                'comments': "an arbitrary comment"
            },
        }
        with pytest.raises(ValueError):
            Oil(str(whoops))

    def test_empty_oil_id(self):
        """ you must specify at least an oil_id """
        with pytest.raises(TypeError):
            Oil(oil_id="")

    def test__id_ignored(self):
        """
        checks that the an _id attribute of a dict will get ignored
        """
        oil = Oil.from_py_json({
            'oil_id': "XX123456",
            '_id': 1234567,
            'metadata': {
                'name': "An oil name"
            },
        })

        assert oil.oil_id == "XX123456"

        with pytest.raises(AttributeError):
            _id = oil._id

        assert oil.metadata.name == "An oil name"

        joil = oil.py_json()

        assert '_id' not in joil

    def test_repr_minimal(self):
        """
        The repr should be reasonable
        """
        oil = Oil("XX00000")

        result = repr(oil)

        assert result.startswith("Oil(")
        assert "oil_id='XX00000'" in result

    def test_repr_full(self):
        """
        The repr should be reasonable

        This is a "full" record
        """
        oil = Oil.from_py_json(BIG_RECORD)

        result = repr(oil)

        assert result.startswith("Oil(")
        assert "oil_id='EC02234'" in result

    def test_init_minimal(self):
        """
        Even though we initialized with only an ID, all attributes
        should be present.
        """
        oil = Oil(oil_id=OIL_ID)
        assert oil.oil_id == OIL_ID

        for attr in ('oil_id', 'metadata', 'sub_samples',
                     'status', 'extra_data'):
            assert hasattr(oil, attr)

    def test_add_new_attribute(self):
        """
        You should not be able to add an arbitrary new attribute
        """
        oil = Oil(oil_id=OIL_ID)

        with pytest.raises(AttributeError):
            oil.random_attr = 456

    def test_json_minimal(self):
        """
        When we convert our dataclass into a JSON struct, empty fields
        will be sparse.  The field will not be included in the struct.
        So if we create an Oil with only a name, it will look like this:

            {'name': 'A name for an oil'}
        """
        oil = Oil(oil_id=OIL_ID)
        assert oil.oil_id == OIL_ID

        py_json = oil.py_json()

        assert py_json["oil_id"] == OIL_ID
        assert py_json['adios_data_model_version'] == str(ADIOS_DATA_MODEL_VERSION)
        print(py_json)
        assert len(py_json) == 3

    def test_json_minimal_nonsparse(self):
        oil = Oil(oil_id=OIL_ID)
        py_json = oil.py_json(sparse=False)
        pprint(py_json)

        assert len(py_json) == 8

        for attr in [
                'oil_id',
                'adios_data_model_version',
                'metadata',
                'sub_samples',
                'status',
                'permanent_warnings',
                'extra_data',
                'review_status',
        ]:
            assert attr in py_json

    def test_from_py_json_nothing(self):
        """
        You must specify at least an oil_id
        """
        py_json = {}

        with pytest.raises(TypeError):
            _oil = Oil.from_py_json(py_json)

    def test_from_py_json_minimal(self):
        """
        Note: It seems we are not only checking for existence, but specific
              values.  Parametrize??
        """
        py_json = {"oil_id": OIL_ID}
        oil = Oil.from_py_json(py_json)

        assert oil.oil_id == OIL_ID
        assert oil.status == []
        assert oil.metadata.API is None

    def test_subsamples(self):
        """
        Is it getting all the subsamples
        """
        oil = Oil.from_py_json(BIG_RECORD)

        print("working with:", oil.metadata.name)

        assert len(oil.sub_samples) == 5
        assert oil.sub_samples[0].metadata.name == "Fresh Oil Sample"
        assert oil.sub_samples[3].metadata.name == "25.3% Evaporated"

    def test_permanent_warnings(self):
        oil = Oil('XXXXXX')

        warn = "Something is very wrong with this record."
        oil.permanent_warnings.append(warn)
        print(oil)

        msgs = oil.validate()

        print(msgs)

        assert "W000: " + warn in msgs


class TestMetaData:
    def test_init_empty(self):
        meta = MetaData()

        for attr in ('location', 'reference', 'sample_date', 'product_type',
                     'API', 'comments', 'labels'):
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
        ('reference', Reference(year=1999, reference='reference text'),
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
        }),
        ('comments', 'some comment', {
            'default': '',
            'value': 'some comment',
        }),
        ('labels', ['heavy'], {
            'default': [],
            'value': ['heavy'],
        }),
    ))
    def test_metadata_in_oil(self, attr, value, expected):
        oil = Oil(oil_id=OIL_ID)

        assert hasattr(oil.metadata, attr)
        assert getattr(oil.metadata, attr) == expected['default']

        setattr(oil.metadata, attr, value)
        assert getattr(oil.metadata, attr) == expected['value']


class TestFullRecordMetadata:
    """
    tests loading a full record (or pretty full) from JSON
    """
    oil = Oil.from_py_json(BIG_RECORD)

    def test_oil_id(self):
        oil = self.oil

        print(oil.oil_id)
        assert oil.oil_id == "EC02234"

    @pytest.mark.parametrize("attr, value", [
        ("location", "Canada, Alberta"),
        ('name', 'Access West Blend Winter'),
        ('source_id', '2234'),
        ('sample_date', '2013-08-04'),
    ])
    def test_location(self, attr, value):
        metadata = self.oil.metadata

        print(vars(metadata))
        assert getattr(metadata, attr) == value


def test_from_file_name():
    """
    test loading a Oil object directly from a file name
    """
    oil = Oil.from_file(TEST_DATA_DIR / "EC" / "EC02234.json")

    # maybe it would be better to do more of a test,
    # but the full loading should be tested elsewhere
    assert oil.oil_id == "EC02234"


def test_from_file():
    """
    test loading a Oil object directly from an open file
    """
    oil = Oil.from_file(open(TEST_DATA_DIR / "EC" / "EC02234.json",
                             encoding="utf-8"))

    # maybe it would be better to do more of a test,
    # but the full loading should be tested elsewhere
    assert oil.oil_id == "EC02234"


def test_to_file_name():
    """
    test saving an oil object to a filename
    """
    oil = Oil.from_py_json(BIG_RECORD)
    oil.to_file(OUTPUT_DIR / "temp_to_file.json")

    # read it back as JSON
    with open(OUTPUT_DIR / "temp_to_file.json", encoding="utf-8") as infile:
        data = json.load(infile)

    assert data["oil_id"] == 'EC02234'


def test_to_open_file():
    """
    test saving an oil object to a filename
    """
    oil = Oil.from_py_json(BIG_RECORD)
    oil.to_file(open(OUTPUT_DIR / "temp_to_file.json", 'w', encoding="utf-8"))

    # read it back as JSON
    with open(OUTPUT_DIR / "temp_to_file.json", encoding="utf-8") as infile:
        data = json.load(infile)

    assert data["oil_id"] == 'EC02234'


def test_round_trip():
    """
    tests that a large Oil object loaded from JSON, then saved as JSON,
    then reloaded again, results in an equal object

    Not really much a test at this point, but why not?
    """
    filein = TEST_DATA_DIR / "EC" / "EC00506.json"
    fileout = OUTPUT_DIR / "temp_oil.json"

    # read it in:
    oilin = Oil.from_file(filein)

    # check that they are not exactly the same
    # this used to be a test for when we had equal data written in
    # different order it's not longer valid
    oilin.to_file(fileout)

    # read the new one to an Oil object
    oilout = Oil.from_file(fileout)

    assert oilin == oilout


def test_version_none():
    """
    If it doesn't have a version string, it should get the current one.
    """
    oil = Oil('XXXXXX')
    oil.metadata.name = 'An oil name'
    pyjs = oil.py_json()

    # remove the version:
    pyjs.pop('adios_data_model_version', None)

    oil = Oil.from_py_json(pyjs)

    assert oil.adios_data_model_version == ADIOS_DATA_MODEL_VERSION


def test_version_bad():
    """
    If it doesn't have a valid version string, it should raise an error.
    """
    pyjs = {
        'oil_id': 'AD00123',
        'adios_data_model_version': 1.2,
        'metadata': {
            'name': 'An oil name'
        }
    }
    with pytest.raises(ValueError):
        _oil = Oil.from_py_json(pyjs)


# this fails because it will try to load it anyway
# after running through the updaters
# and only raise an error if it can't load.
@pytest.mark.xfail
def test_version_too_high():
    pyjs = {
        'oil_id': 'AD00123',
        'adios_data_model_version': "2.0.0",
        'metadata': {
            'name': 'An oil name'
        }
    }
    with pytest.raises(VersionError):
        _oil = Oil.from_py_json(pyjs)
