"""
Functional tests for the Model Web API
"""
from .base import FunctionalTestBase


class DistinctTests(FunctionalTestBase):
    def test_get_distinct(self):
        resp = self.testapp.get('/distinct')
        distinct = resp.json_body

        assert 'location' in [f['column'] for f in distinct]
        assert 'product_type' in [f['column'] for f in distinct]

        for v in [f['values'] for f in distinct]:
            assert len(v) > 0
