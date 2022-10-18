"""
Configuration setup for pytest tests.
"""
import pytest
from webtest import TestApp

from adios_db.test.test_session.test_session import restore_test_db
from adios_db_api import main


TEST_SETTINGS = {
    'cors_policy.origins': ('http://0.0.0.0:8080\n'
                            'http://localhost:8080'),
    'pyramid.default_locale_name': 'en',
    'pyramid.includes': ('pyramid_tm\n'
                         'cornice'),
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_authorization': 'false',
    'pyramid.reload_templates': 'true',
    'mongodb.host': 'localhost',
    'mongodb.port': '27017',
    'mongodb.database': 'adios_db_test',
    'mongodb.alias': 'oil-db-app',
    'caps.can_modify_db': 'true',
    'install_path': '.',
    'help_dir': './help',
    'user_docs_dir': '../user_docs',
}


# pytest fixture for testing
# alternative to the test baseclass defined in base.py
@pytest.fixture
def testapp():
    """
    webtest application object suitable for testing
    """
    restore_test_db(TEST_SETTINGS)
    app = main(None, **TEST_SETTINGS)
    return TestApp(app)
