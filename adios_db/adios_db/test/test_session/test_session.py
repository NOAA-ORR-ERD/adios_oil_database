import os
from pathlib import Path

import pytest

from adios_db.models.oil.oil import Oil

from adios_db.util.db_connection import connect_mongodb
from adios_db.scripts.db_initialize import init_db
from adios_db.scripts.db_restore import restore_db


here = Path(__file__).resolve().parent

# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost

pytestmark = pytest.mark.mongo


class SessionTestBase:
    settings = {'mongodb.host': 'localhost',
                'mongodb.port': '27017',
                'mongodb.database': 'adios_db_test',
                'mongodb.alias': 'oil-db-app',
                }

    @classmethod
    def setup_class(cls):
        '''
            Here we setup the database we will use for testing our session.
            - Make a connection to the mongodb server
            - Init the database
            - Load a set of test data into the database
        '''
        # print('\nsetup_class()...')

        restore_db(cls.settings, os.path.join(here, 'test_data'))

    @classmethod
    def teardown_class(cls):
        'Clean up any data the model generated after running tests.'
        # print('\nteardown_class()...')
        init_db(cls.settings, show_prompt=False)

    @classmethod
    def deep_get(cls, obj, attr_path, default=None):
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        attrs, current = attr_path, obj

        try:
            for p in attrs:
                current = current[p]

            return current
        except KeyError:
            return default


class TestSessionQuery(SessionTestBase):
    def test_init(self):
        session = connect_mongodb(self.settings)

        assert hasattr(session, 'query')  # our object, not mongodb

    def test_query(self):
        session = connect_mongodb(self.settings)

        recs = session.query()

        assert len(recs) == 26  # our test set size

    def test_query_with_projection(self):
        session = connect_mongodb(self.settings)

        recs = session.query(projection=['metadata.name'])

        assert len(recs) == 26  # our test set size

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

        recs = session.query(oil_id='AD00020')

        assert len(recs) == 1
        assert recs[0]['oil_id'] == 'AD00020'

    def test_query_by_name_location(self):
        session = connect_mongodb(self.settings)

        q_text = 'Alaska North Slope'
        recs = list(session.query(text=q_text))

        assert len(recs) == 3

        for rec in recs:
            assert q_text.lower() in rec['metadata']['name'].lower()

        q_text = 'Saudi Arabia'
        *recs, = session.query(text=q_text)

        assert len(recs) == 4

        for rec in recs:
            assert q_text.lower() in rec['metadata']['location'].lower()

    @pytest.mark.parametrize('labels, expected', [
        (['Crude', 'Medium'], ['Crude', 'Medium']),
        ('Crude,Medium', ['Crude', 'Medium']),
        ('Crude, Medium', ['Crude', 'Medium']),
    ])
    def test_query_by_labels(self, labels, expected):
        session = connect_mongodb(self.settings)

        *recs, = session.query(labels=labels)

        assert len(recs) == 6

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

        *recs, = session.query(api=api)

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
        '''
            Note: MongoDB 3.6 has changed how they compare array fields in a
                  sort.  It used to compare the arrays element-by-element,
                  continuing until any "ties" were broken.  Now it only
                  compares the highest/lowest valued element, apparently
                  ignoring the rest.
                  For this reason, a MongoDB query will not properly sort our
                  status and labels array fields, at least not in a simple way.
        '''
        session = connect_mongodb(self.settings)

        *recs, = session.query(sort=[(field, direction)],
                               projection=['metadata.labels'])

        assert len(recs) == 26

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
        (0, 26),
        (10, 16),
        ([20, 30], 6),
        ('0,10', 10),
        ('0, 10', 10),
    ])
    def test_query_with_paging(self, page, expected):
        session = connect_mongodb(self.settings)

        *recs, = session.query(page=page)

        assert len(recs) == expected


class TestSessionInserting(SessionTestBase):
    """
    testing adding oil records to the DB
    """
    def test_add_one_record(self):
        session = connect_mongodb(self.settings)

        ID = "XX00000"
        # create a minimal oil
        oil = Oil(ID)

        # add it:
        session.insert_oil_record(oil)

        result = list(session.query(oil_id=ID))

        assert len(result) == 1
        assert result[0]['oil_id'] == ID
