"""
Functional tests for the Vocabulary Web API
"""
from .base import FunctionalTestBase


class VocabularyTests(FunctionalTestBase):
    """
    Vocabulary is simply a query of the list of known vocabulary words
    for a set list of categories {'compounds', 'industry_properties'}
    """
    def test_get_no_category(self):
        self.testapp.get('/vocabulary/', status=404)

    def test_get_bad_category(self):
        self.testapp.get('/vocabulary/other_stuff/', status=404)

    def test_get_good_category(self):
        resp = self.testapp.get('/vocabulary/compounds/')
        words = resp.json_body

        for w in ('Benzene',):
            assert w in words

    def test_get_bad_partial_word(self):
        resp = self.testapp.get('/vocabulary/compounds/?wf=bogus')
        words = resp.json_body

        assert len(words) == 0

        resp = self.testapp.get('/vocabulary/industry_properties/?wf=bogus')
        words = resp.json_body

        assert len(words) == 0

    def test_get_good_partial_word(self):
        """
        This test is dependent on the words that are in the vocabulary lists.
        And so a good test result might change if the data set changes.
        """
        resp = self.testapp.get('/vocabulary/compounds/?wf=pris')
        words = resp.json_body

        assert len(words) == 1
        for w in words:
            assert 'pris' in w.lower()

        resp = self.testapp.get('/vocabulary/industry_properties/?wf=conrad')
        words = resp.json_body

        assert len(words) == 3
        for w in words:
            assert 'conrad' in w.lower()
