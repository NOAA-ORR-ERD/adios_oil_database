"""
base.py: Base classes for different types of tests.
"""
import os

from unittest import TestCase
from webtest import TestApp

from adios_db.test.test_session.test_session import restore_test_db

from adios_db_api import main

from .conftest import TEST_SETTINGS


class FunctionalTestBase(TestCase):

    def setUp(self):
        here = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.dirname(here))

        # self.settings = self.get_settings()
        self.settings = TEST_SETTINGS

        restore_test_db(self.settings)
        app = main(None, **self.settings)

        self.testapp = TestApp(app)

    def tearDown(self):
        """
        Clean up any data the model generated after running tests.
        """
        pass
