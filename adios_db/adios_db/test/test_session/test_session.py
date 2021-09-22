import os
from pathlib import Path

import pytest

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.product_type import types_to_labels

try:
    from adios_db.util.db_connection import connect_mongodb
    from adios_db.scripts.db_initialize import init_db
    from adios_db.scripts.db_restore import restore_db
except ModuleNotFoundError:
    pass  # we don't want this to fail if these tests are skipped

here = Path(__file__).resolve().parent

test_data = here.parent / "data_for_testing" / "noaa-oil-data"
# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost

pytestmark = pytest.mark.mongo


def restore_test_db(settings):
    restore_db(settings, test_data)


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

        restore_test_db(cls.settings)

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
        (['Crude Oil', 'Medium Crude'], ['Crude Oil', 'Medium Crude']),
        ('Crude Oil,Medium Crude', ['Crude Oil', 'Medium Crude']),
        ('Crude Oil, Medium Crude', ['Crude Oil', 'Medium Crude']),
    ])
    def test_query_by_labels(self, labels, expected):
        session = connect_mongodb(self.settings)

        recs = session.query(labels=labels)

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


class TestSessionGetOil(SessionTestBase):
    def test_init(self):
        session = connect_mongodb(self.settings)

        assert hasattr(session, 'get_oil')

    def test_get(self):
        session = connect_mongodb(self.settings)

        for _id in ('AD00020',):
            rec = session.get_oil(_id)

            assert rec is not None

            for attr in ('oil_id', 'adios_data_model_version',
                         'metadata', 'status', 'review_status'):
                assert attr in rec

    def test_get_no_record(self):
        session = connect_mongodb(self.settings)

        rec = session.get_oil('bogus')

        assert rec is None


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
        assert session.get_labels(-1) is None
        assert session.get_labels('-1') is None

        # test an id that can't even be used
        with pytest.raises(ValueError):
            session.get_labels('bogus')


class TestSessionInsertOil(SessionTestBase):
    '''
        testing adding oil records to the DB
    '''
    def test_new_oil_id(self):
        '''
            The function new_oil_id() is related to insertion, so we put the
            test here inside the insertion class scope
        '''
        session = connect_mongodb(self.settings)

        oil_id = session.new_oil_id()
        print(f'new_oil_id: {oil_id}')

        assert oil_id[:2] == 'XX'

        # add a new oil using the oil id we got from new_oil_id()
        oil = Oil(oil_id)
        session.insert_oil(oil)

        # new oil ID sequence should be incremented
        oil_seq = int(oil_id[2:])
        new_oil_seq = int(session.new_oil_id()[2:])

        assert new_oil_seq > oil_seq
        assert new_oil_seq - oil_seq == 1

    def test_insert_oil_obj(self):
        session = connect_mongodb(self.settings)

        ID = session.new_oil_id()
        # create a minimal oil
        oil = Oil(ID)

        session.insert_oil(oil)

        result = list(session.query(oil_id=ID))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == ID

    def test_insert_json_obj(self):
        session = connect_mongodb(self.settings)

        ID = session.new_oil_id()
        # create a minimal oil
        oil = Oil(ID)

        session.insert_oil(oil.py_json())

        result = list(session.query(oil_id=ID))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == ID

    def test_insert_oil_obj_none_id(self):
        '''
            This test case is a bit contrived since an oil object must be
            instantiated with a valid ID.  Still, an insert operation should
            be able to handle this situation without problems.
        '''
        session = connect_mongodb(self.settings)

        # create a minimal oil
        oil = Oil('bogus')
        oil.oil_id = None

        oil_id = session.insert_oil(oil)['oil_id']
        print(f'new oil_id: {oil_id}')

        result = list(session.query(oil_id=oil_id))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == oil_id

    def test_insert_oil_obj_empty_id(self):
        '''
            This test case is a bit contrived since an oil object must be
            instantiated with a valid ID.  Still, an insert operation should
            be able to handle this situation without problems.
        '''
        session = connect_mongodb(self.settings)

        # create a minimal oil
        oil = Oil('bogus')
        oil.oil_id = ''

        oil_id = session.insert_oil(oil)['oil_id']
        print(f'new oil_id: {oil_id}')

        result = list(session.query(oil_id=oil_id))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == oil_id

    def test_insert_json_obj_no_id(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        json_obj = Oil('bogus').py_json()
        del json_obj['oil_id']

        oil_id = session.insert_oil(json_obj)['oil_id']
        print(f'new oil_id: {oil_id}')

        result = list(session.query(oil_id=oil_id))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == oil_id

    def test_insert_json_obj_none_id(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        json_obj = Oil('bogus').py_json()
        json_obj['oil_id'] = None

        oil_id = session.insert_oil(json_obj)['oil_id']
        print(f'new oil_id: {oil_id}')

        result = list(session.query(oil_id=oil_id))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == oil_id

    def test_insert_json_obj_empty_id(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        json_obj = Oil('bogus').py_json()
        json_obj['oil_id'] = ''

        oil_id = session.insert_oil(json_obj)['oil_id']
        print(f'new oil_id: {oil_id}')

        result = list(session.query(oil_id=oil_id))

        assert len(result) == 1

        new_oil = result[0]
        print(f'new_oil.keys(): {new_oil.keys()}')
        assert new_oil['oil_id'] == oil_id


class TestSessionDeleteOil(SessionTestBase):
    '''
        testing deleting oil records from the DB
    '''
    def test_delete_oil(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        oil = Oil('bogus')
        oil.oil_id = None

        oil_id = session.insert_oil(oil)['oil_id']
        print(f'new oil_id inserted: {oil_id}')

        # now we delete the oil
        ret = session.delete_oil(oil_id)

        assert ret == 1


class TestSessionUpdateOil(SessionTestBase):
    '''
        testing updating oil records in the DB
    '''
    def test_update_oil_obj(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        oil = Oil('bogus')
        oil.oil_id = None

        oil_id = session.insert_oil(oil)['oil_id']
        print(f'new oil_id inserted: {oil_id}')

        # now we update the oil
        oil.metadata.name = 'New Name'
        updated_oil = session.update_oil(oil)

        assert updated_oil['metadata']['name'] == 'New Name'

    def test_update_json_obj(self):
        session = connect_mongodb(self.settings)

        # create a minimal oil
        oil = Oil('bogus')
        oil.oil_id = None

        oil_id = session.insert_oil(oil)['oil_id']
        print(f'new oil_id inserted: {oil_id}')

        # now we update the oil
        oil.metadata.name = 'New Name'
        updated_oil = session.update_oil(oil.py_json())

        assert updated_oil['metadata']['name'] == 'New Name'
