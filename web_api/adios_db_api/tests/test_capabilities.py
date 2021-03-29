"""
Functional tests for the Model Web API
"""
from .base import FunctionalTestBase


class CapabilitiesTests(FunctionalTestBase):
    '''
        Capabilities is simply a query of what the server is configured
        to be able to do.
        So we will verify the available options.
    '''
    def test_get_capabilities(self):
        resp = self.testapp.get('/capabilities/')
        caps = resp.json_body

        assert caps[0]['can_modify_db'] == 'true'

        resp = self.testapp.get('/capabilities/0/')
        caps = resp.json_body

        assert caps['can_modify_db'] == 'true'
