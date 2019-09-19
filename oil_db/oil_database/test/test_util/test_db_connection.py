import pytest

from oil_database.util.db_connection import connect_mongodb


@pytest.fixture
def mongodb_settings():
    '''
        These should be pretty normal default MongoDB settings.
    '''
    return {'mongodb.host': 'localhost',
            'mongodb.port': 27017,
            'mongodb.database': 'oil_database',
            'mongodb.alias': 'oil-db-app'}


def test_connect_mongodb(mongodb_settings):
    '''
        Test a successful MongoDB connection.  We need to have a running
        MongoDB server for this to pass.
    '''
    mongodb_client = connect_mongodb(mongodb_settings)

    assert mongodb_client.address == ('localhost', 27017)


def test_mongodb_connect_exceptions():
    with pytest.raises(KeyError):
        connect_mongodb({})

    with pytest.raises(KeyError):
        connect_mongodb({'mongodb.host': 'localhost'})  # port setting missing

    with pytest.raises(TypeError):
        connect_mongodb({'mongodb.host': 'localhost',
                         'mongodb.port': '27017'  # should be an int
                         })
