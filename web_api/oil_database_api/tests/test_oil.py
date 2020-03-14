"""
Functional tests for the Model Web API

FIXME: WE should hve tests that test the API, not everything else!

And getting sample_oils from the oil filemaker data makes me really nervous



"""
import copy

from .base import FunctionalTestBase
from .sample_oils import basic_noaa_fm


class OilTestBase(FunctionalTestBase):
    '''
        This class just defines some functions for evaluating parts of the oil
        content.  They are not pytests in and of themselves, but return a
        valid status.
    '''
    def api_valid(self, api_gravity):
        for k in ('gravity',):
            if k not in api_gravity:
                return False

        if not isinstance(api_gravity['gravity'], (float)):
            return False

        return True

    def densitiy_valid(self, density):
        for k in ('ref_temp', 'density'):
            if k not in density:
                return False

        if not self.ref_temp_valid(density['ref_temp']):
            return False

        if not self.density_value_valid(density['density']):
            return False

        return True

    def dvis_valid(self, dvis):
        for k in ('ref_temp', 'viscosity'):
            if k not in dvis:
                return False

        if not self.ref_temp_valid(dvis['ref_temp']):
            return False

        if not self.dvis_value_valid(dvis['viscosity']):
            return False

        return True

    def kvis_valid(self, kvis):
        for k in ('ref_temp', 'viscosity'):
            if k not in kvis:
                return False

        if not self.ref_temp_valid(kvis['ref_temp']):
            return False

        if not self.kvis_value_valid(kvis['viscosity']):
            return False

        return True

    def cut_valid(self, cut):
        for k in ('fraction', 'vapor_temp'):
            if k not in cut:
                return False

        if not self.unit_value_valid(cut['fraction'], ('1', 'fraction', '%')):
            return False

        if not self.ref_temp_valid(cut['vapor_temp']):
            return False

        return True

    def ift_valid(self, ift):
        for k in ('tension', 'ref_temp', 'interface'):
            if k not in ift:
                return False

        if not self.ift_value_valid(ift['tension']):
            return False

        if not self.ref_temp_valid(ift['ref_temp']):
            return False

        if not ift['interface'] in ('air', 'water', 'seawater'):
            return False

        # all other fields can be blank

        return True

    def sulfur_valid(self, sulfur):
        for k in ('fraction',):
            if k not in sulfur:
                return False

        if not self.unit_value_valid(sulfur['fraction'],
                                     ('1', 'fraction', '%')):
            return False

        return True

    def flash_point_valid(self, fp):
        for k in ('ref_temp',):
            if k not in fp:
                print('flash point: missing attr: {}', k)
                return False

        if not self.ref_temp_valid(fp['ref_temp']):
            print('flash point: ref_temp invalid: ', fp['ref_temp'])
            return False

        return True

    def pour_point_valid(self, pp):
        for k in ('ref_temp',):
            if k not in pp:
                return False

        if not self.ref_temp_valid(pp['ref_temp']):
            return False

        return True

    def adhesion_valid(self, adhesion):
        for k in ('adhesion',):
            if k not in adhesion:
                return False

        if not self.adhesion_value_valid(adhesion['adhesion']):
            return False

        return True

    def water_valid(self, water):
        for k in ('fraction',):
            if k not in water:
                return False

        if not self.fraction_valid(water['fraction']):
            return False

        return True

    def wax_valid(self, wax):
        for k in ('fraction',):
            if k not in wax:
                return False

        if not self.fraction_valid(wax['fraction']):
            return False

        return True

    def toxicity_valid(self, toxicity):
        for k in ('species', 'tox_type'):
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

    def fraction_valid(self, fraction):
        return self.unit_value_valid(fraction, ('1', '%', 'fraction'))

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
        for k in ['_cls', 'unit']:
            if k not in obj:
                return False

        if obj['unit'] not in units:
            return False

        # The min/max pair is sparse if one value is None, so the requirement
        # is that we need to have at least one of these attributes
        if not (any(l in obj for l in ('value', 'min_value', 'max_value'))):
            return False

        # if we have a single value, it needs to be valid
        if ('value' in obj and
                not isinstance(obj['value'], (float, int))):
            return False

        # if we have a ranged value, at least one needs to be valid
        # ex: [10.0, 20.0] -> valid, represents interval 10.0 to 20.0
        #     [10.0, None] -> valid, represents >10.0
        #     [None, 10.0] -> valid, represents <10.0
        if all([k in obj for k in ('min_value', 'max_value')]):
            if not any([isinstance(obj[k], (float, int))
                        for k in ('min_value', 'max_value')]):
                return False

        return True


class OilTests(OilTestBase):
    def test_get_no_id(self):
        """
        This request should result in an empty list,
        so that's all we can test for
        """
        resp = self.testapp.get('/oils')
        oils = resp.json_body

        assert oils == []

        # for r in oils:
        #     for k in ('name',
        #               'oil_id',
        #               'status',
        #               'location',
        #               'product_type',
        #               'apis',
        #               'pour_point',
        #               'viscosity',
        #               'categories',
        #               'categories_str'):
        #         assert k in r

    def test_get_invalid_id(self):
        self.testapp.get('/oils/{}'.format('bogus'), status=404)

    def test_get_valid_id(self):
        '''
            We are basing our tests on webtest(unittest), so parametrization
            doesn't work.

            General Rule: if a record doesn't have data to fill an attribute,
                          the attribute should probably not exist either.
                          So if we find an attribute, we will test it assuming
                          that it has something valid.
        '''
        for oil_id in ('AD00009',
                       'AD00020',
                       'AD00025',
                       'AD01759',
                       'EC002234',
                       'EC000506',
                       'EC000561'):
            resp = self.testapp.get('/oils/{0}'.format(oil_id))
            oil = resp.json_body

            print('oil: ', oil['_id'])

            # print (ujson.dumps(oil, indent=4, ensure_ascii=False))

            # the oil_database module has its own tests for all the oil
            # attributes, but we need to test that we conform to it.
            attrs = ['_id',
                     'oil_id',
                     'name',
                     'product_type',
                     'location',
                     'reference',
                     'reference_date',
                     'comments',
                     'labels',
                     'status',
                     'samples']

            for k in attrs:
                assert k in oil

            sample = [s for s in oil['samples']
                      if s['name'] == 'Fresh Oil Sample'][0]

            assert any(k in sample for k in ('apis', 'densities'))

            if 'apis' in sample:
                for a in sample['apis']:
                    assert self.api_valid(a)

            if 'densities' in sample:
                for d in sample['densities']:
                    assert self.densitiy_valid(d)

            assert any(k in sample for k in ('kvis', 'dvis'))

            if 'dvis' in sample:
                for dvis in sample['dvis']:
                    assert self.dvis_valid(dvis)

            if 'kvis' in sample:
                for kvis in sample['kvis']:
                    assert self.kvis_valid(kvis)

            if 'cuts' in sample:
                for c in sample['cuts']:
                    assert self.cut_valid(c)

            if 'ifts' in sample:
                for i in sample['ifts']:
                    assert self.ift_valid(i)

            if 'pour_point' in sample:
                assert self.pour_point_valid(sample['pour_point'])

            if 'flash_point' in sample:
                assert self.flash_point_valid(sample['flash_point'])

            if 'adhesion' in sample:
                assert self.adhesion_valid(sample['adhesion'])

            if 'water' in sample:
                assert self.water_valid(sample['water'])

            if 'wax_content' in sample:
                assert self.wax_valid(sample['wax_content'])

            if 'sulfur' in sample:
                assert self.sulfur_valid(sample['sulfur'])

            if 'toxicities' in sample:
                for t in sample['toxicities']:
                    assert self.toxicity_valid(t)

    def test_post_no_payload(self):
        self.testapp.post_json('/oils', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/oils', status=400)

    def test_post_bad_req(self):
        self.testapp.post_json('/oils', params=[], status=400)
        self.testapp.post_json('/oils', params=1, status=400)
        self.testapp.post_json('/oils', params='asdf', status=400)

        self.testapp.request('/oils', method='POST',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.post_json('/oils', params={"bad": 'attr'}, status=415)

    def test_put_bad_req(self):
        self.testapp.put_json('/oils', params=[], status=400)
        self.testapp.put_json('/oils', params=1, status=400)
        self.testapp.put_json('/oils', params='asdf', status=400)

        self.testapp.request('/oils', method='PUT',
                             body=b'{"malformed":',
                             headers={'Content-Type': 'application/json'},
                             status=400)

        self.testapp.put_json('/oils', params={"bad": 'attr'}, status=415)

    def test_delete_bad_req(self):
        self.testapp.delete('/oils/{}'.format('bogus_id'), status=404)

    def test_crud(self):
        oil_json = copy.deepcopy(basic_noaa_fm)

        #
        # test not inserted
        #
        self.testapp.get('/oils/{}'.format(oil_json['oil_id']), status=404)

        #
        # insert
        #
        resp = self.testapp.post_json('/oils', params=oil_json)
        oil_json = resp.json_body

        assert oil_json['_id'] == 'AD99999'
        assert oil_json['apis'][0]['gravity'] == 28.0

        #
        # test inserted
        #
        resp = self.testapp.get('/oils/{0}'.format(oil_json['_id']))
        oil_json = resp.json_body

        assert oil_json['_id'] == 'AD99999'
        assert oil_json['apis'][0]['gravity'] == 28.0

        #
        # update
        #
        oil_json['apis'][0]['gravity'] = 33.0

        resp = self.testapp.put_json('/oils', params=oil_json)
        oil_json = resp.json_body

        assert oil_json['apis'][0]['gravity'] == 33.0

        #
        # test updated
        #
        resp = self.testapp.get('/oils/{0}'.format(oil_json['_id']))
        oil_json = resp.json_body

        assert oil_json['apis'][0]['gravity'] == 33.0

        #
        # delete
        #
        self.testapp.delete('/oils/{}'.format(oil_json['_id']))

        #
        # test deleted
        #
        self.testapp.get('/oils/{}'.format(oil_json['_id']), status=404)


class TestOilSort(OilTestBase):
    """
    testing calls to the API asking for sorted results

    This only tests sorting on API and name -- probably should. test them all
    """

    def test_sorted_by_name_desc(self):
        """
        check getting a sorted result by name -- decending order
        """
        resp = self.testapp.get("/oils?dir=desc&limit=5&page=0&q=&qApi=&qLabels=&sort=name")

        result = resp.json_body
        names = [rec['name'] for rec in result]

        # we are sorting case insensitive
        assert names == sorted(names, reverse=True, key=lambda x: x.lower())

    def test_sorted_by_name_asc(self):
        """
        check getting a sorted result by name -- ascending order
        """
        resp = self.testapp.get("/oils?dir=asc&limit=5&page=0&q=&qApi=&qLabels=&sort=name")

        result = resp.json_body
        names = [rec['name'] for rec in result]

        # we are sorting case insensitive
        assert names == sorted(names, reverse=False, key=lambda x: x.lower())

    def test_sorted_by_api_and_range(self):
        """
        check getting results sorted by API, with a sub-range

        https://adios-stage.orr.noaa.gov/api/oils?dir=asc&limit=20&page=0&q=&qApi=26%2C50&qLabels=&sort=api

        We really should build up the url from parameters, but I'm lazy now.
        """

        resp = self.testapp.get("/oils?dir=asc&limit=20&page=0&q=&qApi=26%2C50&qLabels=&sort=api")

        result = resp.json_body

        apis = [rec['api'] for rec in result]

        assert max(apis) <= 50
        assert min(apis) >= 26

        assert apis == sorted(apis)

