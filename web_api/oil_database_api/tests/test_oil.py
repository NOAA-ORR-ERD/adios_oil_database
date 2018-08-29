"""
Functional tests for the Model Web API
"""
from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class OilTests(FunctionalTestBase):
    def test_get_oil_no_id(self):
        resp = self.testapp.get('/oil')
        oils = resp.json_body

        for r in oils:
            for k in ('adios_oil_id',
                      'api',
                      'categories',
                      'field_name',
                      'location',
                      'name',
                      'oil_class',
                      'pour_point',
                      'product_type',
                      'viscosity'):
                assert k in r

    def test_get_oil_invalid_id(self):
        self.testapp.get('/oil/{}'.format('bogus'), status=404)

    def test_get_oil_valid_id(self):
        resp = self.testapp.get('/oil/{0}'.format('AD00009'))
        oil = resp.json_body

        # the oil_database module has its own tests for all the oil
        # attributes, but we need to test that we conform to it.
        for k in ('name',
                  'api',
                  'oil_water_interfacial_tension_n_m',
                  'oil_water_interfacial_tension_ref_temp_k',
                  'oil_seawater_interfacial_tension_n_m',
                  'oil_seawater_interfacial_tension_ref_temp_k',
                  'pour_point_min_k',
                  'pour_point_max_k',
                  'flash_point_min_k',
                  'flash_point_max_k',
                  'emulsion_water_fraction_max',
                  'bullwinkle_time',
                  'bullwinkle_fraction',
                  'adhesion_kg_m_2',
                  'sulphur_fraction',
                  'solubility',
                  ):
            assert k in oil

        for c in oil['cuts']:
            for k in ('fraction',
                      'liquid_temp_k',
                      'vapor_temp_k'):
                assert k in c

        for d in oil['densities']:
            for k in ('kg_m_3',
                      'ref_temp_k',
                      'weathering'):
                assert k in d

        for kvis in oil['kvis']:
            for k in ('m_2_s',
                      'ref_temp_k',
                      'weathering'):
                assert k in kvis
