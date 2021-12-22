"""
Tests of mongo connections

These require a mongo db to be running.

They will only run if the --mongo command line option is passed to pytest.

NOTE: These should really use a fixture to start up mongo, and/or
      mocking of the DB.
"""
import pytest

# Pass the --mongo command line option if you want these to run.
pytestmark = pytest.mark.mongo

try:
    from adios_db.util.db_connection import connect_mongodb
except ModuleNotFoundError:
    pass  # Don't want to error out if these tests are skipped


@pytest.fixture
def mongodb_settings():
    """
    These should be pretty normal default MongoDB settings.
    """
    return {'mongodb.host': 'localhost',
            'mongodb.port': 27017,
            'mongodb.database': 'adios_db',
            'mongodb.alias': 'oil-db-app'}


def test_connect_mongodb(mongodb_settings):
    """
    Test a successful MongoDB connection.  We need to have a running
    MongoDB server for this to pass.
    """
    mongodb_client = connect_mongodb(mongodb_settings)

    assert mongodb_client.address == ('localhost', 27017)


def test_mongodb_connect_exceptions():
    with pytest.raises(KeyError):
        connect_mongodb({})

    with pytest.raises(KeyError):
        connect_mongodb({'mongodb.host': 'localhost'})  # port setting missing
