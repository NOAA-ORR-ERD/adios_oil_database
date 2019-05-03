"""
Functional tests for the Model Web API
"""
from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class OilTestBase(FunctionalTestBase):
    '''
        This class just defines some functions for evaluating parts of the oil
        content.  They are not pytests in and of themselves, but return a
        valid status.
    '''
    def api_valid(self, api_gravity):
        for k in ('_cls',
                  'gravity',
                  'weathering'):
            if k not in api_gravity:
                return False

        if not isinstance(api_gravity['gravity'], (float)):
            return False

        if not isinstance(api_gravity['weathering'], (float)):
            return False

        return True

    def densitiy_valid(self, density):
        for k in ('_cls',
                  'ref_temp',
                  'density',
                  'weathering'):
            if k not in density:
                return False

        if not self.ref_temp_valid(density['ref_temp']):
            return False

        if not self.density_value_valid(density['density']):
            return False

        if not isinstance(density['weathering'], (float)):
            return False

        return True

    def dvis_valid(self, dvis):
        for k in ('_cls',
                  'ref_temp',
                  'viscosity',
                  'weathering'):
            if k not in dvis:
                return False

        if not self.ref_temp_valid(dvis['ref_temp']):
            return False

        if not self.dvis_value_valid(dvis['viscosity']):
            return False

        if not isinstance(dvis['weathering'], (float)):
            return False

        return True

    def kvis_valid(self, kvis):
        for k in ('_cls',
                  'ref_temp',
                  'viscosity',
                  'weathering'):
            if k not in kvis:
                return False

        if not self.ref_temp_valid(kvis['ref_temp']):
            return False

        if not self.kvis_value_valid(kvis['viscosity']):
            return False

        if not isinstance(kvis['weathering'], (float)):
            return False

        return True

    def cut_valid(self, cut):
        for k in ('_cls',
                  'fraction',
                  'vapor_temp',
                  'weathering'):
            if k not in cut:
                return False

        if not self.unit_value_valid(cut['fraction'], ('1',)):
            return False

        if not self.ref_temp_valid(cut['vapor_temp']):
            return False

        if not isinstance(cut['weathering'], (float)):
            return False

        return True

    def ift_valid(self, ift):
        for k in ('_cls',
                  'tension',
                  'ref_temp',
                  'interface',
                  'weathering',
                  # 'method',  # can be blank
                  # 'replicates',  # can be blank
                  # 'standard_deviation'  # can be blank
                  ):
            if k not in ift:
                return False

        if not self.ift_value_valid(ift['tension']):
            return False

        if not self.ref_temp_valid(ift['ref_temp']):
            return False

        if not ift['interface'] in ('air', 'water', 'seawater'):
            return False

        if not isinstance(ift['weathering'], (float)):
            return False

        # all other fields can be blank

        return True

    def sulfur_valid(self, sulfur):
        for k in ('_cls',
                  'fraction',
                  'weathering',
                  ):
            if k not in sulfur:
                return False

        if not self.unit_value_valid(sulfur['fraction'], ('1',)):
            return False

        if not isinstance(sulfur['weathering'], (float)):
            return False

        return True

    def flash_point_valid(self, fp):
        for k in ('_cls',
                  'min_temp',
                  'max_temp',
                  'weathering',
                  ):
            if k not in fp:
                return False

        if not self.ref_temp_valid(fp['min_temp']):
            return False

        if not self.ref_temp_valid(fp['max_temp']):
            return False

        if not isinstance(fp['weathering'], (float)):
            return False

        return True

    def pour_point_valid(self, pp):
        for k in ('_cls',
                  'min_temp',
                  'max_temp',
                  'weathering',
                  ):
            if k not in pp:
                return False

        if not self.ref_temp_valid(pp['min_temp']):
            return False

        if not self.ref_temp_valid(pp['max_temp']):
            return False

        if not isinstance(pp['weathering'], (float)):
            return False

        return True

    def adhesion_valid(self, adhesion):
        for k in ('_cls',
                  'adhesion',
                  'weathering',
                  ):
            if k not in adhesion:
                return False

        if not self.adhesion_value_valid(adhesion['adhesion']):
            return False

        if not isinstance(adhesion['weathering'], (float)):
            return False

        return True

    def toxicity_valid(self, toxicity):
        for k in ('_cls',
                  'species',
                  'tox_type',
                  ):
            if k not in toxicity:
                return False

        if not toxicity['tox_type'].lower() in ('ec', 'lc'):
            return False

        # these attrs can be optionally blank, but not all of them
        if not any([k in toxicity
                    for k in ('after_24h', 'after_48h', 'after_96h')]):
            return False

        for k in ('after_24h', 'after_48h', 'after_96h'):
            if k in toxicity:
                if not isinstance(toxicity[k], (float)):
                    return False

        return True

    def ref_temp_valid(self, ref_temp):
        return self.unit_value_valid(ref_temp, ('C', 'K'))

    def density_value_valid(self, density_value):
        return self.unit_value_valid(density_value,
                                     ('g/cm^3', 'g/L', 'g/mL', 'kg/m^3',
                                      'lbs/ft^3', 'api', 'S', 'SG'))

    def dvis_value_valid(self, dvis_value):
        return self.unit_value_valid(dvis_value,
                                     ('Pa.s', 'Pa s', 'mPa.s', 'mPa s',
                                      'N s/m^2', 'dyne s/cm^2',
                                      'kg/(m s)', 'g/(cm s)',
                                      'p', 'cP',))

    def kvis_value_valid(self, kvis_value):
        return self.unit_value_valid(kvis_value,
                                     ('St', 'cSt',
                                      'm^2/s', 'cm^2/s', 'mm^2/s', 'in^2/s'))

    def ift_value_valid(self, ift_value):
        return self.unit_value_valid(ift_value,
                                     ('N/m', 'mN/m',
                                      'dyne/cm', 'gf/cm',
                                      'erg/cm^2', 'erg/mm^2',
                                      'pdl/in', 'lbf/in'))

    def adhesion_value_valid(self, adhesion_value):
        return self.unit_value_valid(adhesion_value,
                                     ('Pa', 'kPa', 'MPa', 'N/m^2',
                                      'g/m^2', 'gf/m^2',
                                      'g/cm^2', 'gf/cm^2',
                                      'kg/m^2', 'kgf/m^2',
                                      'kgf/cm^2', 'kg/cm^2',
                                      'lb/in^2', 'lbf/in^2',
                                      'psi', 'pfsi',
                                      'dyn/cm^2',
                                      'bar', 'bars', 'mbar'))

    def unit_value_valid(self, obj, units):
        '''
            Generic test of our unit/value objects.  We have a lot of them,
            so this should cover the general testing criteria.
        '''
        for k in ['_cls', 'value', 'unit']:
            if k not in obj:
                return False

        if obj['unit'] not in units:
            return False

        if not isinstance(obj['value'], (float)):
            return False

        return True


class OilTests(OilTestBase):
    def test_get_oil_no_id(self):
        resp = self.testapp.get('/oil')
        oils = resp.json_body

        for r in oils:
            for k in ('name',
                      'oil_id',
                      'status',
                      'location',
                      'product_type',
                      'apis',
                      'pour_point',
                      'viscosity',
                      'categories',
                      'categories_str'):
                assert k in r

    def test_get_oil_invalid_id(self):
        self.testapp.get('/oil/{}'.format('bogus'), status=404)

    def test_get_oil_valid_id(self):
        '''
            We are basing our tests on webtest(unittest), so parametrization
            doesn't work.
        '''
        for oil_id in ('AD00009',
                       'AD00020',
                       'AD00025',
                       'AD01759'):
            resp = self.testapp.get('/oil/{0}'.format(oil_id))
            oil = resp.json_body

            print ('oil:')
            pp.pprint(oil)

            # the oil_database module has its own tests for all the oil
            # attributes, but we need to test that we conform to it.
            attrs = ['_cls',
                     '_id',
                     'name',
                     'location',
                     'comments',
                     'reference',
                     'reference_date',
                     'product_type',
                     'categories',
                     'status',
                     'apis',
                     'densities',
                     'dvis',
                     'kvis',
                     'cuts',
                     'ifts',
                     'pour_points',
                     'flash_points',
                     'adhesions',
                     'alkanes',
                     'alkylated_pahs',
                     'benzene',
                     'biomarkers',
                     'ccme',
                     'ccme_f1',
                     'ccme_f2',
                     'ccme_tph',
                     'chromatography',
                     'conradson',
                     'corexit',
                     'emulsions',
                     'evaporation_eqs',
                     'headspace',
                     'sara_total_fractions',
                     'sulfur',
                     'toxicities',
                     'water',
                     'wax_content']

            for k in attrs:
                assert k in oil

            for a in oil['apis']:
                assert self.api_valid(a)

            for d in oil['densities']:
                assert self.densitiy_valid(d)

            for dvis in oil['dvis']:
                assert self.dvis_valid(dvis)

            for kvis in oil['kvis']:
                assert self.kvis_valid(kvis)

            for c in oil['cuts']:
                assert self.cut_valid(c)

            for i in oil['ifts']:
                assert self.ift_valid(i)

            for s in oil['sulfur']:
                assert self.sulfur_valid(s)

            for f in oil['flash_points']:
                assert self.flash_point_valid(f)

            for p in oil['pour_points']:
                assert self.pour_point_valid(p)

            for a in oil['adhesions']:
                assert self.adhesion_valid(a)

            for t in oil['toxicities']:
                assert self.toxicity_valid(t)

    def test_post_oil(self):
        '''
            Not implemented yet.
        '''
        self.testapp.post('/oil', status=501)

    def test_put_oil(self):
        '''
            Not implemented yet.
        '''
        self.testapp.put('/oil', status=501)

    def test_delete_oil(self):
        '''
            Not implemented yet.
        '''
        self.testapp.delete('/oil', status=501)
