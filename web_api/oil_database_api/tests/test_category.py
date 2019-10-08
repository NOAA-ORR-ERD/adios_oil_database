"""
Functional tests for the Model Web API
"""
import copy

from .base import FunctionalTestBase
from .sample_oils import basic_noaa_fm


class CategoryTestBase(FunctionalTestBase):
    '''
        This class just defines some functions for evaluating parts of the oil
        content.  They are not pytests in and of themselves, but return a
        valid status.
    '''
    pass


class CategoryTests(CategoryTestBase):
    def test_get_no_id(self):
        resp = self.testapp.get('/category')
        categories = resp.json_body

        for c in categories:
            for k in ('name',
                      '_id',
                      # 'parent',  # optional
                      'children'):
                assert k in c

    def test_get_invalid_id(self):
        self.testapp.get('/category/{}'.format('bogus_id'), status=404)

    def test_get_valid_id(self):
        '''
            We are basing our tests on webtest(unittest), so parametrization
            doesn't work.

            Category IDs are random UUIDS.  So we can't really choose a static
            known ID.  We need to retrieve the IDs
        '''
        res = self.testapp.get('/category')
        categories = res.json_body

        for c in categories:
            c_id = c['_id']
            res = self.testapp.get('/category/{}'.format(c_id))
            cat = res.json_body

            assert c_id == cat['_id']

    def test_post_no_payload(self):
        self.testapp.post_json('/category', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/category', status=400)

    def test_post_bad_req(self):
        self.testapp.post_json('/category', params=[], status=400)
        self.testapp.post_json('/category', params=1, status=400)
        self.testapp.post_json('/category', params='asdf', status=400)

        self.testapp.request('/category', method='POST',
                             body='{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.post_json('/category', params={"bad": 'attr'}, status=415)

    def test_put_bad_req(self):
        self.testapp.put_json('/category', params=[], status=400)
        self.testapp.put_json('/category', params=1, status=400)
        self.testapp.put_json('/category', params='asdf', status=400)

        self.testapp.request('/category', method='PUT',
                             body='{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.put_json('/category', params={"bad": 'attr'}, status=415)

    def test_delete_bad_req(self):
        self.testapp.delete('/oil/{}'.format('bogus_id'), status=404)

    def test_crud(self):
        cat_json = {'name': 'Test Category'}

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
        resp = self.testapp.post_json('/category', params=cat_json)
        cat_json = resp.json_body

        assert all([k in cat_json for k in ('_id', 'name')])
        assert cat_json['name'] == 'Test Category'

        #
        # test inserted
        #
        resp = self.testapp.get('/category/{0}'.format(cat_json['_id']))
        cat_json = resp.json_body

        assert all([k in cat_json for k in ('_id', 'name')])
        assert cat_json['name'] == 'Test Category'

        #
        # update
        #
        cat_json['name'] = 'Updated Test Category'

        resp = self.testapp.put_json('/category', params=cat_json)
        cat_json = resp.json_body

        assert cat_json['name'] == 'Updated Test Category'

        #
        # test updated
        #
        resp = self.testapp.get('/category/{0}'.format(cat_json['_id']))
        cat_json = resp.json_body

        assert cat_json['name'] == 'Updated Test Category'

        #
        # delete
        #
        self.testapp.delete('/category/{}'.format(cat_json['_id']))

        #
        # test deleted
        #
        self.testapp.get('/category/{}'.format(cat_json['_id']), status=404)
