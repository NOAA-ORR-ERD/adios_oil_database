"""
Configuration setup for pytest tests.
"""

import pytest
from webtest import TestApp
from webtest.app import AppError

from oil_database_api import main


SETTINGS = {'cors_policy.origins': ('http://0.0.0.0:8080\n'
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
            'mongodb.database': 'oil_database',
            'mongodb.alias': 'oil-db-app',
            'caps.can_modify_db': 'false',
            'install_path': '.',
            'help_dir': './help'
            }


@pytest.fixture
def testapp():
    """
    webtest application object suitable for testing
    """
    app = main(None, **SETTINGS)
    return TestApp(app)


