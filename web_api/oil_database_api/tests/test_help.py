"""
Functional tests for the Model Web API
"""
from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class HelpTests(FunctionalTestBase):
    '''
        This is a help/feedback system based on the webgnome product.
        we will just test the basic functionality here.
    '''
    def test_get_help(self):
        help_res = self.testapp.get('/help').json_body

        for r in help_res:
            for k in ('html', 'keywords', 'path'):
                assert k in r

    def test_get_help_with_path(self):
        help_res = self.testapp.get('/help/views/form/oil').json_body

        for k in ('html', 'path'):
            assert k in help_res

    def test_post_help_with_index(self):
        '''
            index is supplied
        '''
        params = {'index': 1}
        res = self.testapp.post_json('/help', params=params).json_body

        assert res['index'] == 1

        res = self.testapp.post_json('/help', params=params).json_body

        assert res['index'] == 1

    def test_post_help_no_index(self):
        '''
            index should autoincrement server-side if none supplied
        '''
        params = {}
        res = self.testapp.post_json('/help', params=params).json_body

        count = res['index']

        res = self.testapp.post_json('/help', params=params).json_body

        assert res['index'] == count + 1

    def test_post_help_different_urls(self):
        '''
            Researching WebGnomeClient, it seems that the json payload is the
            only thing that is important on a POST or PUT
            And the index is intended to only increment the first time a
            help page is given feedback
        '''
        params = {}
        res1 = self.testapp.post_json('/help', params=params).json_body

        res2 = self.testapp.post_json('/help', params=res1).json_body

        assert res1['index'] == res2['index']
