"""
Functional tests for the Model Web API
"""
from .base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class CapabilitiesTests(FunctionalTestBase):
    '''
        Capabilities is simply a query of what the server is configured
        to be able to do.
        So we will verify the available options.
    '''
    def test_get_capabilities(self):
        resp = self.testapp.get('/capabilities')
        caps = resp.json_body

        print(caps)

        assert caps['can_modify_db'] == 'false'
