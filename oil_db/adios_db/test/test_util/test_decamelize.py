
import pytest

from oil_database.util.decamelize import (separate_camelcase,
                                          camelcase_to_sep,
                                          camelcase_to_space,
                                          camelcase_to_underscore)


class TestCamelCase(object):
    @pytest.mark.parametrize('value, expected',
                             [
                              ('Area', ['Area']),
                              ('OilConcentration', ['Oil', 'Concentration']),
                              ('ConcentrationInWater', ['Concentration',
                                                        'In',
                                                        'Water']),
                              ('concentrationInWater', ['In', 'Water']),
                              ('ABCImportedRecordDEF', ['ABC',
                                                        'Imported',
                                                        'Record',
                                                        'DEF']),
                              ])
    def test_separate_camelcase(self, value, expected):
        words = separate_camelcase(value)

        assert words == expected

    @pytest.mark.parametrize('value, sep, lower, expected',
                             [
                              ('Area', ' ', False, 'Area'),
                              ('Area', ' ', True, 'area'),
                              ('ConcentrationInWater', ' ', False,
                               'Concentration In Water'),
                              ('ConcentrationInWater', ' ', True,
                               'concentration in water'),
                              ('ConcentrationInWater', '-', False,
                               'Concentration-In-Water'),
                              ('ConcentrationInWater', '-', True,
                               'concentration-in-water'),
                              ('ConcentrationInWater', '_', False,
                               'Concentration_In_Water'),
                              ('ConcentrationInWater', '_', True,
                               'concentration_in_water'),
                              ('concentrationInWater', ' ', False, 'In Water'),
                              ('concentrationInWater', ' ', True, 'in water'),
                              ('concentrationInWater', '-', False, 'In-Water'),
                              ('concentrationInWater', '-', True, 'in-water'),
                              ('concentrationInWater', '_', False, 'In_Water'),
                              ('concentrationInWater', '_', True, 'in_water'),
                              ])
    def test_camelcase_to_sep(self, value, sep, lower, expected):
        words = camelcase_to_sep(value, sep=sep, lower=lower)

        assert words == expected

    @pytest.mark.parametrize('value, lower, expected',
                             [
                              ('Area', False, 'Area'),
                              ('OilConcentration', False, 'Oil Concentration'),
                              ('ConcentrationInWater', False,
                               'Concentration In Water'),
                              ('concentrationInWater', False, 'In Water'),
                              ('Area', True, 'area'),
                              ('OilConcentration', True, 'oil concentration'),
                              ('ConcentrationInWater', True,
                               'concentration in water'),
                              ('concentrationInWater', True, 'in water'),
                              ])
    def test_camelcase_to_space(self, value, lower, expected):
        words = camelcase_to_space(value, lower=lower)

        assert words == expected

    @pytest.mark.parametrize('value, lower, expected',
                             [
                              ('Area', False, 'Area'),
                              ('OilConcentration', False, 'Oil_Concentration'),
                              ('ConcentrationInWater', False,
                               'Concentration_In_Water'),
                              ('concentrationInWater', False, 'In_Water'),
                              ('Area', True, 'area'),
                              ('OilConcentration', True, 'oil_concentration'),
                              ('ConcentrationInWater', True,
                               'concentration_in_water'),
                              ('concentrationInWater', True, 'in_water'),
                              ])
    def test_camelcase_to_underscore(self, value, lower, expected):
        words = camelcase_to_underscore(value, lower=lower)

        assert words == expected
