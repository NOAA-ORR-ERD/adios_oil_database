"""
Functional tests for the Model Web API
"""
import pytest

from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class QueryTests(FunctionalTestBase):
    '''
        The query api will accept various posted json payloads corresponding
        to the MongoDB querying grammar.

        We will not test every nuance of querying capabilities, simply that we
        can successfully query the database (and fail predictably).

        Note: It is very tempting to want to parametrize these tests, but our
              class is derived from unittest.TestCase in order to setup and
              teardown the web application.
              This is breaking our ability to parametrize.
    '''
    def test_post_query(self):
        '''
            If we don't specify a table name, the default table that will be
            queried is the oil table.
        '''
        params = {'query': {'adios_oil_id': 'AD00009'}
                  }
        resp = self.testapp.post_json('/query', params=params)
        res = resp.json_body

        print res

        assert len(res) == 1
        assert res[0]['_cls'].endswith('.Oil')

    def test_post_query_no_results(self):
        '''
            Here we perform a query that we expect will return no results.
        '''
        params = {'query': {'adios_oil_id': 'AD99999'}
                  }
        resp = self.testapp.post_json('/query', params=params)
        res = resp.json_body

        print res

        assert len(res) == 0

    def test_post_query_no_query(self):
        '''
            We can't really know how many result items we will get, but we can
            assume it will be non-empty, since our API performs an open ended
            query as a default if none is specified.
        '''
        params = {}
        resp = self.testapp.post_json('/query', params=params)
        res = resp.json_body

        assert len(res) > 0

    def test_post_query_oil(self):
        params = {'table': 'oil',
                  'query': {'adios_oil_id': 'AD00009'}
                  }
        resp = self.testapp.post_json('/query', params=params)
        res = resp.json_body

        print res

        assert len(res) == 1
        assert res[0]['_cls'].endswith('.Oil')

    def test_post_query_imported_record(self):
        params = {'table': 'imported_record',
                  'query': {'adios_oil_id': 'AD00009'}
                  }
        resp = self.testapp.post_json('/query', params=params)
        res = resp.json_body

        print res

        assert len(res) == 1
        assert res[0]['_cls'].endswith('.ImportedRecord')

    def test_post_query_ec_imported_record(self):
        params = {'table': 'ec_imported_record',
                  'query': {'oil_id': 'EC002712'}
                  }
        resp = self.testapp.post_json('/query', params=params)
        res = resp.json_body

        print res

        assert len(res) == 1
        assert res[0]['_cls'].endswith('.ECImportedRecord')
