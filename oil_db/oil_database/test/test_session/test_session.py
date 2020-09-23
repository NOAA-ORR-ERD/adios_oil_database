import os
from pathlib import Path

import pytest

from oil_database.util.db_connection import connect_mongodb
from oil_database.scripts.db_initialize import init_db
from oil_database.scripts.db_restore import restore_db

here = Path(__file__).resolve().parent


class SessionTestBase:
    settings = {'mongodb.host': 'localhost',
                'mongodb.port': '27017',
                'mongodb.database': 'oil_database_test',
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
        print('\nsetup_class()...')

        restore_db(cls.settings, os.path.join(here, 'test_data'))

    @classmethod
    def teardown_class(cls):
        'Clean up any data the model generated after running tests.'
        print('\nteardown_class()...')
        init_db(cls.settings, show_prompt=False)


class TestSessionQuery(SessionTestBase):
    def test_init(self):
        session = connect_mongodb(self.settings)

        assert hasattr(session, 'query')  # our object, not mongodb

    def test_query(self):
        session = connect_mongodb(self.settings)

        recs = list(session.query())

        assert len(recs) == 26  # our test set size

    def test_query_with_projection(self):
        session = connect_mongodb(self.settings)

        recs = list(session.query(projection=['metadata.name']))

        assert len(recs) == 26  # our test set size

        for rec in recs:
            # We should only get the id plus one field
            # That field should be in the proper context however
            assert len(rec.keys()) == 2
            assert '_id' in rec
            assert 'metadata' in rec

            assert len(rec['metadata'].keys()) == 1
            assert 'name' in rec['metadata']

    def test_query_by_id(self):
        session = connect_mongodb(self.settings)

        recs = list(session.query(oil_id='AD00020'))

        assert len(recs) == 1
        assert recs[0]['_id'] == 'AD00020'

    def test_query_by_name_location(self):
        session = connect_mongodb(self.settings)

        q_text = 'Alaska North Slope'
        recs = list(session.query(text=q_text))

        assert len(recs) == 3

        for rec in recs:
            assert q_text.lower() in rec['metadata']['name'].lower()

        q_text = 'Saudi Arabia'
        recs = list(session.query(text=q_text))

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

        recs = list(session.query(labels=labels))

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

        recs = list(session.query(api=api))

        assert len(recs) == len_results

        for rec in recs:
            _min, _max = expected

            if _min is not None:
                assert rec['metadata']['API'] >= _min

            if _max is not None:
                assert rec['metadata']['API'] <= _max
