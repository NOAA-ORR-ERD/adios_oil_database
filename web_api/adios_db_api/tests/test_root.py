"""
Functional tests for the Model Web API

despite the name, this tests both the root and "about" endpoints
"""
from .base import FunctionalTestBase


# # refactoring this one -- it no longer gives a json reponse.
class RootUrlTests(FunctionalTestBase):
    """
    The top level url is just a welcome message.
    We will enhance this with some package version info later.
    """
#     def test_get_root_url(self):
#         resp = self.testapp.get('/')
#         root = resp.json_body

#         print(root)

#         assert root['Hello'] == ', welcome to the Oil Database API!!'

    def test_get_root_url(self):
        """
        The root url provides a simple html page response

        This is the same as the about url if it's not serving
        the client files.

        This should probably be enhanced some day
        """
        resp = self.testapp.get('/')
        root = resp.text

        assert "NOAA ADIOS Oil Database" in root

    def test_get_about_url(self):
        """
        The about url provides a simple html page response

        This should probably be enhanced some day
        """
        resp = self.testapp.get('/about')
        root = resp.text

        assert "NOAA ADIOS Oil Database" in root
