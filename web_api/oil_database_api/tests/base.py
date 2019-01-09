"""
base.py: Base classes for different types of tests.
"""
import os

from unittest import TestCase
from webtest import TestApp

from oil_database_api import main


class GnomeTestCase(TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.dirname(here))

    def get_settings(self):

        settings = {'cors_policy.origins': ('http://0.0.0.0:8080\n'
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
                    }

        return settings


class FunctionalTestBase(GnomeTestCase):
    def setUp(self):
        super(FunctionalTestBase, self).setUp()

        self.settings = self.get_settings()
        app = main(None, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        'Clean up any data the model generated after running tests.'
        pass
