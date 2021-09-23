"""
Functional tests for the Model Web API

FIXME: We should have tests that test the API, not everything else!
"""

import copy

from .base import FunctionalTestBase
from .sample_oils import basic_noaa_fm

from builtins import isinstance, dict


class OilTestBase(FunctionalTestBase):
    '''
        This class just defines some functions for evaluating parts of the oil
        content.  They are not pytests in and of themselves, but return a
        valid status.
    '''

    def jsonapi_request(self, oil_obj):
        json_obj = {'data': {'attributes': oil_obj}}

        json_obj['data']['type'] = 'oils'

        return json_obj

    def jsonapi_to_oil(self, jsonapi_obj):
        oil_obj = jsonapi_obj['data']['attributes']
        return oil_obj


class OilTests(OilTestBase):
    def test_get_no_id(self):
        """
        This request should result in an empty list,
        so that's all we can test for
        """
        resp = self.testapp.get('/oils/')
        oils = resp.json_body

        assert isinstance(oils, dict)

        for k in ('data', 'meta'):
            assert k in oils

        assert oils['data'] == []

    def test_get_invalid_id(self):
        self.testapp.get('/oils/{}/'.format('bogus'), status=404)

    def test_get_valid_no_options(self):
        '''
            Note: The web server does not have any control over the correctness
                  of the oil records, and so should not have any responsibility
                  for it.  So for this test, we will just test that we did
                  in fact get something that looks like an oil record at a
                  high level.

            Note: We do in fact need to check that we are conforming to the
                  JSON-API specification however.
        '''
        resp = self.testapp.get('/oils/')
        res = resp.json_body

        assert isinstance(res, dict)
        assert 'data' in res
        assert 'meta' in res

        assert 'total' in res['meta']
        assert len(res['data']) == 0
        assert res['meta']['total'] >= 0

    def test_get_valid_with_limit_option(self):
        params = {'limit': 20}
        resp = self.testapp.get('/oils/', params=params)
        res = resp.json_body

        assert isinstance(res, dict)
        assert 'data' in res
        assert 'meta' in res

        assert 'total' in res['meta']
        assert len(res['data']) == 20
        assert res['meta']['total'] >= 20

        for rec in res['data']:
            assert '_id' in rec

            print('\noil attributes: ', rec['attributes'].keys())
            for k in ('metadata',
                      'status'):
                # we are only expecting searchable fields
                assert k in rec['attributes']

    def test_get_valid_id(self):
        '''
            Note: We are basing our tests on webtest(unittest), so
                  parametrization doesn't work.
        '''
        for oil_id in ('AD00009',
                       'AD00020',
                       'AD00025',
                       'EC02234',
                       'EC00506',
                       'EC00561'):
            print(f'checking for {oil_id}')
            resp = self.testapp.get('/oils/{0}'.format(oil_id))
            oil = resp.json_body

            assert isinstance(oil, dict)

            for k in ('data',):
                assert k in oil

            print('oil: ', oil['data']['_id'])

            # The adios_db module has its own tests for all the oil
            # attributes, but we need to test that we conform to it.

            for k in ('oil_id',
                      'metadata',
                      'sub_samples'):
                assert k in oil['data']['attributes']

            # optional status
            if 'status' in oil['data']['attributes']:
                status = oil['data']['attributes']['status']
                assert isinstance(status, list)

            for k in ('name',
                      'source_id',
                      'location',
                      'reference',
                      'product_type',
                      'API'):
                assert k in oil['data']['attributes']['metadata']

            sample = [s for s in oil['data']['attributes']['sub_samples']
                      if s['metadata']['name'] == 'Fresh Oil Sample'][0]

            sample_attrs = ('name',
                            'short_name')
            for k in sample_attrs:
                assert k in sample['metadata']  # required

    def test_post_no_payload(self):
        self.testapp.post_json('/oils/', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/oils/', status=400)

    def test_post_bad_req(self):
        self.testapp.post_json('/oils', params=[], status=307)
        self.testapp.post_json('/oils/', params=[], status=400)
        self.testapp.post_json('/oils/', params=1, status=400)
        self.testapp.post_json('/oils/', params='asdf', status=400)

        self.testapp.request('/oils/', method='POST',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.post_json('/oils/', params={"bad": 'attr'}, status=400)

    def test_put_bad_req(self):
        self.testapp.put_json('/oils', params=[], status=307)
        self.testapp.put_json('/oils/', params=[], status=400)
        self.testapp.put_json('/oils/', params=1, status=400)
        self.testapp.put_json('/oils/', params='asdf', status=400)

        self.testapp.request('/oils/', method='PUT',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.put_json('/oils/', params={"bad": 'attr'}, status=415)

    def test_delete_bad_req(self):
        self.testapp.delete('/oils/{}/'.format('bogus_id'), status=404)


class OilTestCRUD(OilTestBase):

    def test_insert(self):
        oil_json = copy.deepcopy(basic_noaa_fm)

        #
        # Make sure it's not already there
        #
        self.testapp.get('/oils/{}/'.format(oil_json['oil_id']), status=404)
        print(f'test_crud: {oil_json["oil_id"]} is not already there ...')

        #
        # insert
        #
        print(f'inserting {oil_json["oil_id"]}')
        resp = self.testapp.post_json('/oils/',
                                      params=self.jsonapi_request(oil_json))
        oil_json_ret = self.jsonapi_to_oil(resp.json_body)

        assert oil_json_ret['oil_id'] == 'AD99999'
        assert oil_json_ret['metadata']['API'] == 31.7
        print("The post returned the correct record.")

        #
        # test inserted
        #
        print("trying to get:", oil_json['oil_id'])

        resp = self.testapp.get('/oils/{0}'.format(oil_json['oil_id']))
        oil_json_ret = self.jsonapi_to_oil(resp.json_body)

        assert oil_json_ret['oil_id'] == oil_json['oil_id']
        assert oil_json_ret['metadata']['API'] == 31.7

        print(f"get {oil_json['oil_id']} worked after inserting")

    def test_update(self):

        oil_json = copy.deepcopy(basic_noaa_fm)

        print(f'inserting {oil_json["oil_id"]}')
        resp = self.testapp.post_json('/oils/',
                                      params=self.jsonapi_request(oil_json))

        print('testing update...')
        oil_json['metadata']['API'] = 33.0

        resp = self.testapp.put_json('/oils/',
                                     params=self.jsonapi_request(oil_json))
        oil_json_ret = self.jsonapi_to_oil(resp.json_body)

        assert oil_json_ret['metadata']['API'] == 33.0

        #
        # test updated
        #
        print('testing update...')
        resp = self.testapp.get('/oils/{0}'.format(oil_json['oil_id']))
        oil_json_ret = self.jsonapi_to_oil(resp.json_body)

        assert oil_json_ret['metadata']['API'] == 33.0

        print(f"get {oil_json['oil_id']} worked after updating")

    def test_patch(self):

        oil_json = copy.deepcopy(basic_noaa_fm)

        print(f'inserting {oil_json["oil_id"]}')
        resp = self.testapp.post_json('/oils/',
                                      params=self.jsonapi_request(oil_json))

        #
        # patch
        #
        print('testing patch...')
        oil_json['metadata']['API'] = 44.0

        resp = self.testapp.patch_json('/oils/',
                                       params=self.jsonapi_request(oil_json))
        oil_json_ret = self.jsonapi_to_oil(resp.json_body)

        assert oil_json_ret['metadata']['API'] == 44.0

        #
        # test patched
        #
        resp = self.testapp.get('/oils/{0}'.format(oil_json['oil_id']))
        oil_json_ret = self.jsonapi_to_oil(resp.json_body)

        assert oil_json_ret['metadata']['API'] == 44.0

        print(f"get {oil_json['oil_id']} worked after patching")

    def test_delete(self):

        oil_json = copy.deepcopy(basic_noaa_fm)

        print(f'inserting {oil_json["oil_id"]}')
        resp = self.testapp.post_json('/oils/',
                                      params=self.jsonapi_request(oil_json))

        # delete
        #
        print('testing delete...')
        self.testapp.delete('/oils/{}'.format(oil_json['oil_id']))

        # test deleted
        #
        print('test deleted...')
        self.testapp.get('/oils/{}/'.format(oil_json['oil_id']), status=404)

        print("get failed after delete -- and that's good :-)")


class TestOilSort(OilTestBase):
    """
    testing calls to the API asking for sorted results

    This only tests sorting on API and name -- probably should. test them all
    """

    def test_sorted_by_name_desc(self):
        """
        check getting a sorted result by name -- decending order
        """
        resp = self.testapp.get('/oils/?'
                                'limit=5&'
                                'page=0&'
                                'q=&'
                                'qApi=&'
                                'qLabels=&'
                                'dir=desc&'
                                'sort=metadata.name')

        result = resp.json_body['data']
        print(result)
        names = [rec['attributes']['metadata']['name'] for rec in result]

        # we are sorting case insensitive
        assert names == sorted(names, reverse=True, key=lambda x: x.lower())

    def test_sorted_by_name_asc(self):
        """
        check getting a sorted result by name -- ascending order
        """
        resp = self.testapp.get('/oils/?'
                                'limit=5&'
                                'page=0&'
                                'q=&'
                                'qApi=&'
                                'qLabels=&'
                                'dir=asc&'
                                'sort=metadata.name')

        result = resp.json_body['data']
        names = [rec['attributes']['metadata']['name'] for rec in result]

        # we are sorting case insensitive
        assert names == sorted(names, reverse=False, key=lambda x: x.lower())

    def test_sorted_by_api_and_range(self):
        """
        check getting results sorted by API, with a sub-range

        https://adios-stage.orr.noaa.gov/api/oils?dir=asc&limit=20&page=0&q=&qApi=26%2C50&qLabels=&sort=api

        We really should build up the url from parameters, but I'm lazy now.
        """

        resp = self.testapp.get('/oils/?'
                                'dir=asc&'
                                'limit=20&'
                                'page=0&'
                                'q=&'
                                'qApi=26%2C50&'
                                'qLabels=&'
                                'sort=api')

        result = resp.json_body

        apis = [rec['attributes']['metadata']['API'] for rec in result['data']]

        assert min(apis) >= 26
        assert max(apis) <= 50

        assert apis == sorted(apis)
