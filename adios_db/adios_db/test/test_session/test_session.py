from pathlib import Path

import pytest

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.product_type import types_to_labels

# we don't want this to fail if these tests are
# skipped and pymongo is not there.
try:
    import pymongo
except ModuleNotFoundError:
    print("pymongo module not there -- not importing the session modules")
    PYMONGO = False
else:
    PYMONGO = True
    from adios_db.util.db_connection import connect_mongodb

from .session_test_base import SessionTestBase

here = Path(__file__).resolve().parent
test_data = here.parent / "data_for_testing" / "noaa-oil-data"

# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost
pytestmark = pytest.mark.mongo


def test_pymongo():
    """
    Tests to see if pymongo got imported Not really a test, but it should serve
    to give folks a reasonable error message if they try to run the mongo tests
    without pymongo
    """
    assert PYMONGO, "The pymongo package needs to be installed in order to run the mongo tests"


class TestSessionQuery(SessionTestBase):
    def test_init(self):
        session = connect_mongodb(self.settings)

        assert hasattr(session, 'query')  # our object, not mongodb

    def test_query(self):
        session = connect_mongodb(self.settings)

        recs, total = session.query()

        assert len(recs) == 24  # our test set size
        assert total == 24

    def test_query_with_projection(self):
        session = connect_mongodb(self.settings)

        recs, _total = session.query(projection=['metadata.name'])

        assert len(recs) == 24  # our test set size

        for rec in recs:
            # We should only get the oil_id plus one field
            # That field should be in the proper context however
            assert len(rec) == 2
            assert 'oil_id' in rec
            assert 'metadata' in rec

            assert len(rec['metadata']) == 1
            assert 'name' in rec['metadata']

    def test_query_by_id(self):
        session = connect_mongodb(self.settings)

        recs, _total = session.query(oil_id='AD00020')

        assert len(recs) == 1
        assert recs[0]['oil_id'] == 'AD00020'

    def test_query_by_name_location(self):
        session = connect_mongodb(self.settings)

        q_text = 'Alaska North Slope'
        recs, _total = session.query(text=q_text)

        assert len(recs) == 3

        for rec in recs:
            assert q_text.lower() in rec['metadata']['name'].lower()

        q_text = 'Saudi Arabia'
        recs, _total = session.query(text=q_text)

        assert len(recs) == 3

        for rec in recs:
            assert q_text.lower() in rec['metadata']['location'].lower()

    @pytest.mark.parametrize('labels, expected', [
        (['Crude Oil', 'Medium Crude'], ['Crude Oil', 'Medium Crude']),
        ('Crude Oil,Medium Crude', ['Crude Oil', 'Medium Crude']),
        ('Crude Oil, Medium Crude', ['Crude Oil', 'Medium Crude']),
    ])
    def test_query_by_labels(self, labels, expected):
        session = connect_mongodb(self.settings)

        recs, _total = session.query(labels=labels)

        for rec in recs:
            print(rec['metadata']['labels'])

        assert len(recs) > 4  # so it's not too fragile if the data changes

        for rec in recs:
            assert rec['metadata']['labels'] == expected

    @pytest.mark.parametrize('api, len_results, expected', [
        (50, 1, [50, None]),
        ([50], 1, [50, None]),
        ([None, 15], 2, [None, 15]),
        ([10, 15], 2, [10, 15]),
        ('10,15', 2, [10, 15]),
        ('10, 15', 2, [10, 15]),
        ([15, 10], 2, [10, 15]),
    ])
    def test_query_by_api(self, api, len_results, expected):
        session = connect_mongodb(self.settings)

        recs, _total = session.query(api=api)

        assert len(recs) == len_results

        for rec in recs:
            _min, _max = expected

            if _min is not None:
                assert rec['metadata']['API'] >= _min

            if _max is not None:
                assert rec['metadata']['API'] <= _max

    @pytest.mark.parametrize('field, direction', [
        ('_id', 'asc'),
        ('metadata.name', 'asc'),
        ('metadata.name', 'desc'),
        ('metadata.location', 'asc'),
        ('metadata.product_type', 'asc'),
        ('metadata.API', 'asc'),
        ('metadata.sample_date', 'asc'),
        # ('metadata.labels', 'asc'),
        # ('status', 'asc'),
    ])
    def test_query_sort(self, field, direction):
        """
        Note: MongoDB 3.6 has changed how they compare array fields in a
              sort.  It used to compare the arrays element-by-element,
              continuing until any "ties" were broken.  Now it only
              compares the highest/lowest valued element, apparently
              ignoring the rest.
              For this reason, a MongoDB query will not properly sort our
              status and labels array fields, at least not in a simple way.
        """
        session = connect_mongodb(self.settings)

        recs, _total = session.query(sort=[(field, direction)],
                                     projection=['metadata.labels'])

        assert len(recs) == 24

        for rec1, rec2 in zip(recs, recs[1:]):
            value1 = self.deep_get(rec1, field, default=None)
            value2 = self.deep_get(rec2, field, default=None)

            if direction == 'desc':
                if value1 is not None and value2 is not None:
                    assert value1 >= value2
                elif value1 is None and value2 is not None:
                    # None value is less than a real value
                    assert False
            else:
                if value1 is not None and value2 is not None:
                    assert value1 <= value2
                elif value2 is None and value1 is not None:
                    # None value is less than a real value
                    assert False

    @pytest.mark.parametrize('page, expected', [
        ([0, 10], 10),
        ([10, 0], 10),
        (0, 24),
        (10, 14),
        ([20, 30], 4),
        ('0,10', 10),
        ('0, 10', 10),
    ])
    def test_query_with_paging(self, page, expected):
        session = connect_mongodb(self.settings)

        recs, _total = session.query(page=page)

        assert len(recs) == expected


class TestSessionCRUD(SessionTestBase):
    """
    Testing the CRUD operations of our session class
    """
    def test_new_oil_id(self):
        session = connect_mongodb(self.settings)

        oil_id = session.new_oil_id()

        assert isinstance(oil_id, str)
        assert oil_id[:2] == 'XX'
        assert oil_id[2:].isdigit()

    def test_insert_one(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        ID = session.new_oil_id()
        oil = Oil(ID)

        # add it:
        inserted_id = session.insert_one(oil)

        assert inserted_id == ID

    def test_find_one(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        ID = session.new_oil_id()
        oil = Oil(ID)

        # add it:
        session.insert_one(oil)

        new_oil = session.find_one(ID)

        assert new_oil['oil_id'] == ID

    def test_replace_one(self):
        session = connect_mongodb(self.settings)

        ID = session.new_oil_id()
        orig_name = 'original name'
        new_name = 'new name'

        # create a minimal oil
        oil = Oil(ID)
        oil.metadata.name = orig_name

        # add it:
        session.insert_one(oil)

        oil_json = session.find_one(ID)

        assert oil_json['oil_id'] == ID
        assert oil_json['metadata']['name'] == orig_name

        # update it:
        oil.metadata.name = new_name
        res = session.replace_one(oil)
        assert res.matched_count == 1
        assert res.modified_count == 1

        oil_json = session.find_one(ID)

        assert oil_json['oil_id'] == ID
        assert oil_json['metadata']['name'] == new_name

    def test_delete_one(self):
        session = connect_mongodb(self.settings)

        ID = session.new_oil_id()

        # create a minimal oil
        oil = Oil(ID)

        # add it:
        session.insert_one(oil)

        oil_json = session.find_one(ID)

        assert oil_json['oil_id'] == ID

        # delete it:
        session.delete_one(oil.oil_id)

        oil_json = session.find_one(ID)

        assert oil_json is None


class TestSessionGetLabels(SessionTestBase):
    def test_init(self):
        session = connect_mongodb(self.settings)

        assert hasattr(session, 'get_labels')

    def test_all_labels(self):
        session = connect_mongodb(self.settings)

        recs = session.get_labels()

        assert len(recs) == len(types_to_labels.product_types)

    def test_one_label_good(self):
        session = connect_mongodb(self.settings)

        for _id in (0, '0'):
            rec = session.get_labels(_id)

            for attr in ('name', 'product_types'):
                assert attr in rec

    def test_one_label_bad(self):
        session = connect_mongodb(self.settings)

        # test non-existent, but valid IDs
        assert session.get_labels(20000) is None
        assert session.get_labels('20000') is None

        # test an id that can't even be used
        with pytest.raises(ValueError):
            session.get_labels('bogus')

        # test negative id that can't even be used
        with pytest.raises(ValueError):
            session.get_labels(-1)
