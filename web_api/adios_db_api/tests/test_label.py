"""
Functional tests for the Model Web API
"""
from .base import FunctionalTestBase


class LabelTestBase(FunctionalTestBase):
    """
    Just in case we need something later on ...
    """
    pass


class LabelTests(LabelTestBase):
    def test_get_no_id(self):
        resp = self.testapp.get('/labels/')
        labels = resp.json_body

        for c in labels:
            for k in ('_id', 'name'):
                assert k in c

    def test_get_invalid_id(self):
        """
        Testing an ID that can't even be used as an ObjectId
        """
        self.testapp.get('/labels/{}'.format('bogus_id'), status=400)

    def test_get_nonexistent_id(self):
        """
        Here, we are using an ID that can be turned into an ObjectId,
        but it's very unlikely that it will be found in the database.
        """
        self.testapp.get('/labels/{}'.format('10000'), status=307)
        self.testapp.get('/labels/{}/'.format('10000'), status=404)

    def test_get_valid_id(self):
        """
        We are basing our tests on webtest(unittest), so parametrization
        doesn't work.

        Label IDs are random UUIDS.  So we can't really choose a static
        known ID.  We need to retrieve the IDs
        """
        res = self.testapp.get('/labels/')
        labels = res.json_body

        for c in labels:
            c_id = c['_id']
            res = self.testapp.get('/labels/{}/'.format(c_id))
            cat = res.json_body

            assert c_id == cat['_id']
