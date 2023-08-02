"""
Testing the validation framework
"""
from adios_db.models.common.vocabulary import compounds, industry_properties


class TestVocabulary():
    def test_compounds(self):
        """
        The compound list should already be setup upon import
        """
        assert isinstance(compounds, set) > 0
        assert len(compounds) > 0

    def test_industry_properties(self):
        """
        The industry_properties list should already be setup upon import
        """
        assert isinstance(industry_properties, set) > 0
        assert len(industry_properties) > 0
