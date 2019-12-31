"""
Functional tests for the Model Web API
"""
from .base import FunctionalTestBase


class CategoryTestBase(FunctionalTestBase):
    '''
        This class just defines some functions for evaluating parts of the oil
        content.  They are not pytests in and of themselves, but return a
        valid status.
    '''
    pass


class CategoryTests(CategoryTestBase):
    def test_get_no_id(self):
        resp = self.testapp.get('/categories')
        categories = resp.json_body

        for c in categories:
            for k in ('_id', 'name'):
                assert k in c

    def test_get_invalid_id(self):
        '''
            Testing an ID that can't even be used as an ObjectId
        '''
        self.testapp.get('/categories/{}'.format('bogus_id'), status=400)

    def test_get_nonexistent_id(self):
        '''
            Here, we are using an ID that can be turned into an ObjectId,
            but it's very unlikely that it will be found in the database.
        '''
        self.testapp.get('/categories/{}'.format('deadbeefdeadbeefdeadbeef'),
                         status=404)

    def test_get_valid_id(self):
        '''
            We are basing our tests on webtest(unittest), so parametrization
            doesn't work.

            Category IDs are random UUIDS.  So we can't really choose a static
            known ID.  We need to retrieve the IDs
        '''
        res = self.testapp.get('/categories')
        categories = res.json_body

        for c in categories:
            c_id = c['_id']
            res = self.testapp.get('/categories/{}'.format(c_id))
            cat = res.json_body

            assert c_id == cat['_id']

    def test_post_no_payload(self):
        self.testapp.post_json('/categories', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/categories', status=400)

    def test_post_bad_req(self):
        self.testapp.post_json('/categories', params=[], status=400)
        self.testapp.post_json('/categories', params=1, status=400)
        self.testapp.post_json('/categories', params='asdf', status=400)

        self.testapp.request('/categories', method='POST',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.post_json('/categories', params={"bad": 'attr'},
                               status=415)

    def test_put_bad_req(self):
        self.testapp.put_json('/categories', params=[], status=400)
        self.testapp.put_json('/categories', params=1, status=400)
        self.testapp.put_json('/categories', params='asdf', status=400)

        self.testapp.request('/categories', method='PUT',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.put_json('/categories', params={"bad": 'attr'},
                              status=415)

    def test_delete_bad_req(self):
        self.testapp.delete('/categories/{}'.format('bogus_id'), status=400)

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
        resp = self.testapp.post_json('/categories', params=cat_json)
        cat_json = resp.json_body

        assert all([k in cat_json for k in ('_id', 'name')])
        assert cat_json['name'] == 'Test Category'

        #
        # test inserted
        #
        resp = self.testapp.get('/categories/{0}'.format(cat_json['_id']))
        cat_json = resp.json_body

        assert all([k in cat_json for k in ('_id', 'name')])
        assert cat_json['name'] == 'Test Category'

        #
        # update
        #
        cat_json['name'] = 'Updated Test Category'

        resp = self.testapp.put_json('/categories', params=cat_json)
        cat_json = resp.json_body

        assert cat_json['name'] == 'Updated Test Category'

        #
        # test updated
        #
        resp = self.testapp.get('/categories/{0}'.format(cat_json['_id']))
        cat_json = resp.json_body

        assert cat_json['name'] == 'Updated Test Category'

        #
        # delete
        #
        self.testapp.delete('/categories/{}'.format(cat_json['_id']))

        #
        # test deleted
        #
        self.testapp.get('/categories/{}'.format(cat_json['_id']), status=404)
