"""
Functional tests for the Model Web API
"""
from .base import FunctionalTestBase


class RootUrlTests(FunctionalTestBase):
    '''
        The top level url is just a welcome message.
        We will enhance this with some package version info later.
    '''
    def test_get_root_url(self):
        resp = self.testapp.get('/')
        root = resp.json_body

        print(root)

        assert root['Hello'] == ', welcome to the Oil Database API!!'
