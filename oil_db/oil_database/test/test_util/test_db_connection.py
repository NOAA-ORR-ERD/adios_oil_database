import pytest

import pymodm

from oil_database.util.db_connection import connect_mongodb, connect_modm


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


def test_connect_modm(mongodb_settings):
    connect_modm(mongodb_settings)

    assert list(pymodm.connection._CONNECTIONS.keys()) == ['oil-db-app']
    assert (pymodm.connection._CONNECTIONS['oil-db-app']
            .conn_string == 'mongodb://localhost:27017/oil_database')


def test_connect_modm_bad_host(mongodb_settings):
    '''
        Test a condition of bad host information.
        It's important to note that we don't really get a failure right away
        if the host information is wrong.
    '''
    connect_modm({'mongodb.host': 'bogushost',
                  'mongodb.port': 27017,
                  'mongodb.database': 'oil_database',
                  'mongodb.alias': 'oil-db-app'
                  })

    assert list(pymodm.connection._CONNECTIONS.keys()) == ['oil-db-app']
    assert (pymodm.connection._CONNECTIONS['oil-db-app']
            .conn_string == 'mongodb://bogushost:27017/oil_database')


def test_modm_connect_exceptions():
    with pytest.raises(KeyError):
        connect_modm({})

    with pytest.raises(KeyError):
        connect_modm({'mongodb.host': 'localhost'})

    with pytest.raises(KeyError):
        connect_modm({'mongodb.host': 'localhost',
                      'mongodb.port': 27017
                      })

    with pytest.raises(KeyError):
        connect_modm({'mongodb.host': 'localhost',
                      'mongodb.port': 27017,
                      'mongodb.database': 'oil_database'
                      })
