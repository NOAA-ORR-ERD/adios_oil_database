'''
    Test our SARA model classes
'''
import pytest
# pytestmark = pytest.mark.skipif(True, reason="Not using SARA now")


from pydantic import ValidationError

from oil_database.models.common import SARAFraction, SARADensity, MolecularWeight


class TestSaraFraction():
    @pytest.mark.parametrize('sara_type, fraction',
                             [
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Saturates', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Saturates', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ('Saturates', 0.1),
                              ])
    def test_init_required(self, sara_type, fraction):
        if sara_type is None and fraction is None:
            sara_obj = SARAFraction()
        elif fraction is None:
            sara_obj = SARAFraction(sara_type=sara_type)
        elif sara_type is None:
            sara_obj = SARAFraction(fraction=fraction)
        else:
            sara_obj = SARAFraction(sara_type=sara_type, fraction=fraction)

        assert sara_obj.sara_type.value == sara_type
        assert sara_obj.fraction == fraction

    def test_init_defaults(self):
        sara_obj = SARAFraction(sara_type='Aromatics', fraction=0.1)

        assert sara_obj.ref_temp_k == 273.15
        assert sara_obj.weathering == 0.0
        assert sara_obj.standard_deviation is None
        assert sara_obj.replicates is None
        assert sara_obj.method is None

    @pytest.mark.parametrize('ref_temp, weathering, std_dev, replicates, method',
                             [
                              (288.15, 0.1, 0.1, 1.0, 'method'),
                              ('288.15', '0.1', '0.1', '1.0', 0xdeadbeef),
                              pytest.param(
                                  'nope', 0.1, 0.1, 1.0, 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 'nope', 0.1, 1.0, 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 0.1, 'nope', 1.0, 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 0.1, 0.1, 'nope', 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, ref_temp, weathering,
                           std_dev, replicates, method):
        sara_obj = SARAFraction(sara_type='Aromatics', fraction=0.1,
                                ref_temp_k=ref_temp,
                                weathering=weathering,
                                standard_deviation=std_dev,
                                replicates=replicates,
                                method=method)

        assert sara_obj.ref_temp_k == float(ref_temp)
        assert sara_obj.weathering == float(weathering)
        assert sara_obj.standard_deviation == float(std_dev)
        assert sara_obj.replicates == float(replicates)
        assert sara_obj.method == str(method)


class TestSaraDensity():
    @pytest.mark.parametrize('sara_type, kg_m_3',
                             [
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 1000.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Saturates', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 1000.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Saturates', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ('Saturates', 1000.0),
                              ])
    def test_init_required(self, sara_type, kg_m_3):
        if sara_type is None and kg_m_3 is None:
            sara_obj = SARADensity()
        elif kg_m_3 is None:
            sara_obj = SARADensity(sara_type=sara_type)
        elif sara_type is None:
            sara_obj = SARADensity(kg_m_3=kg_m_3)
        else:
            sara_obj = SARADensity(sara_type=sara_type, kg_m_3=kg_m_3)

        assert sara_obj.sara_type.value == sara_type
        assert sara_obj.kg_m_3 == kg_m_3

    def test_init_defaults(self):
        sara_obj = SARADensity(sara_type='Aromatics', kg_m_3=1000.0)

        assert sara_obj.ref_temp_k == 273.15
        assert sara_obj.weathering == 0.0

    @pytest.mark.parametrize('ref_temp, weathering',
                             [
                              (288.15, 0.1),
                              ('288.15', '0.1'),
                              pytest.param(
                                  'nope', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, ref_temp, weathering):
        sara_obj = SARADensity(sara_type='Aromatics', kg_m_3=1000.0,
                               ref_temp_k=ref_temp,
                               weathering=weathering)

        assert sara_obj.ref_temp_k == float(ref_temp)
        assert sara_obj.weathering == float(weathering)


class TestMolecularWeight():
    @pytest.mark.parametrize('sara_type, g_mol',
                             [
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 100.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Saturates', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 100.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Saturates', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ('Saturates', 100.0),
                              ])
    def test_init_required(self, sara_type, g_mol):
        if sara_type is None and g_mol is None:
            sara_obj = MolecularWeight()
        elif g_mol is None:
            sara_obj = MolecularWeight(sara_type=sara_type)
        elif sara_type is None:
            sara_obj = MolecularWeight(g_mol=g_mol)
        else:
            sara_obj = MolecularWeight(sara_type=sara_type, g_mol=g_mol)

        assert sara_obj.sara_type.value == sara_type
        assert sara_obj.g_mol == g_mol

    def test_init_defaults(self):
        sara_obj = MolecularWeight(sara_type='Aromatics', g_mol=1000.0)

        assert sara_obj.ref_temp_k == 273.15
        assert sara_obj.weathering == 0.0

    @pytest.mark.parametrize('ref_temp, weathering',
                             [
                              (288.15, 0.1),
                              ('288.15', '0.1'),
                              pytest.param(
                                  'nope', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, ref_temp, weathering):
        sara_obj = MolecularWeight(sara_type='Aromatics', g_mol=1000.0,
                                   ref_temp_k=ref_temp,
                                   weathering=weathering)

        assert sara_obj.ref_temp_k == float(ref_temp)
        assert sara_obj.weathering == float(weathering)
