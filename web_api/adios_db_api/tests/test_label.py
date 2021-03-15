"""
Functional tests for the Model Web API
"""
import pytest

from .base import FunctionalTestBase


class LabelTestBase(FunctionalTestBase):
    '''
        This class just defines some functions for evaluating parts of the oil
        content.  They are not pytests in and of themselves, but return a
        valid status.
    '''
    pass


class LabelTests(LabelTestBase):
    def test_get_no_id(self):
        resp = self.testapp.get('/labels/')
        labels = resp.json_body

        for c in labels:
            for k in ('_id', 'name'):
                assert k in c

    def test_get_invalid_id(self):
        '''
            Testing an ID that can't even be used as an ObjectId
        '''
        self.testapp.get('/labels/{}'.format('bogus_id'), status=400)

    def test_get_nonexistent_id(self):
        '''
            Here, we are using an ID that can be turned into an ObjectId,
            but it's very unlikely that it will be found in the database.
        '''
        self.testapp.get('/labels/{}'.format('1000'), status=307)
        self.testapp.get('/labels/{}/'.format('1000'), status=404)

    def test_get_valid_id(self):
        '''
            We are basing our tests on webtest(unittest), so parametrization
            doesn't work.

            Label IDs are random UUIDS.  So we can't really choose a static
            known ID.  We need to retrieve the IDs
        '''
        res = self.testapp.get('/labels/')
        labels = res.json_body

        for c in labels:
            c_id = c['_id']
            res = self.testapp.get('/labels/{}/'.format(c_id))
            cat = res.json_body

            assert c_id == cat['_id']

    # For the moment, we are hard-coding the labels to match a .csv file
    # in the adios_db python package.  So we can't perform any modifications.
    # The labels might go back into the database sometime though, so instead of
    # deleting these tests, we will skip them.
    @pytest.mark.skip
    def test_post_no_payload(self):
        self.testapp.post_json('/labels', status=400)

    @pytest.mark.skip
    def test_put_no_payload(self):
        self.testapp.put_json('/labels', status=400)

    @pytest.mark.skip
    def test_post_bad_req(self):
        self.testapp.post_json('/labels', params=[], status=400)
        self.testapp.post_json('/labels', params=1, status=400)
        self.testapp.post_json('/labels', params='asdf', status=400)

        self.testapp.request('/labels', method='POST',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.post_json('/labels', params={"bad": 'attr'},
                               status=415)

    @pytest.mark.skip
    def test_put_bad_req(self):
        self.testapp.put_json('/labels', params=[], status=400)
        self.testapp.put_json('/labels', params=1, status=400)
        self.testapp.put_json('/labels', params='asdf', status=400)

        self.testapp.request('/labels', method='PUT',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.put_json('/labels', params={"bad": 'attr'},
                              status=415)

    @pytest.mark.skip
    def test_delete_bad_req(self):
        self.testapp.delete('/labels/{}'.format('bogus_id'), status=400)

    @pytest.mark.skip
    def test_crud(self):
        lbl_json = {'name': 'Test Label'}

        #
        # test not inserted
        # Note: For categories, the PK is a UUID.  So we can't practically
        #       test if our category already exists.
        #
        # self.testapp.get('/category/{}'.format(cat_json['oil_id']),
        #                  status=404)

        #
        # insert
        #
        resp = self.testapp.post_json('/labels', params=lbl_json)
        lbl_json = resp.json_body

        assert all([k in lbl_json for k in ('_id', 'name')])
        assert lbl_json['name'] == 'Test Label'

        #
        # test inserted
        #
        resp = self.testapp.get('/labels/{0}'.format(lbl_json['_id']))
        lbl_json = resp.json_body

        assert all([k in lbl_json for k in ('_id', 'name')])
        assert lbl_json['name'] == 'Test Label'

        #
        # update
        #
        lbl_json['name'] = 'Updated Test Label'

        resp = self.testapp.put_json('/labels', params=lbl_json)
        lbl_json = resp.json_body

        assert lbl_json['name'] == 'Updated Test Label'

        #
        # test updated
        #
        resp = self.testapp.get('/labels/{0}'.format(lbl_json['_id']))
        lbl_json = resp.json_body

        assert lbl_json['name'] == 'Updated Test Label'

        #
        # delete
        #
        self.testapp.delete('/labels/{}'.format(lbl_json['_id']))

        #
        # test deleted
        #
        self.testapp.get('/labels/{}'.format(lbl_json['_id']), status=404)
