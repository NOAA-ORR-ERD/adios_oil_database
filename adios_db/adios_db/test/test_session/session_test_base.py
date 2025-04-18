from pathlib import Path

# we don't want this to fail if these tests are
# skipped and pymongo is not there.
try:
    import pymongo
except ModuleNotFoundError:
    print("pymongo module not there -- not importing the session modules")
    PYMONGO = False
else:
    PYMONGO = True
    from adios_db.scripts.db_initialize import init_db
    from adios_db.scripts.db_restore import restore_db


here = Path(__file__).resolve().parent
test_data = here.parent / "data_for_testing" / "noaa-oil-data"


def restore_test_db(settings):
    restore_db(settings, test_data)


class SessionTestBase:
    settings = {'mongodb.host': 'localhost',
                'mongodb.port': '27017',
                'mongodb.database': 'adios_db_test',
                'mongodb.alias': 'oil-db-app',
                'gridfs.buckets': ['attachments'],
                }

    @classmethod
    def setup_class(cls):
        """
        Here we setup the database we will use for testing our session.
        - Make a connection to the mongodb server
        - Init the database
        - Load a set of test data into the database
        """
        # print('\nsetup_class()...')

        restore_test_db(cls.settings)

    @classmethod
    def teardown_class(cls):
        """
        Clean up any data the model generated after running tests.
        """
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
