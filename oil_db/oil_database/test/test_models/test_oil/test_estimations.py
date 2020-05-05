'''
    Test our Oil Model Estimations class
'''
import pytest

from oil_database.util.json import ObjFromDict
from oil_database.data_sources.oil.estimations import (OilEstimation,
                                                       OilSampleEstimation)
from oil_database.models.common.float_unit import TemperatureUnit

np = docutils = pytest.importorskip("numpy")


class TestOilEstimation():
    @pytest.mark.parametrize(
        'oil',
        [{'name': 'Oil Name'},
         {'oil_name': 'Oil Name'},
         pytest.param(None, marks=pytest.mark.raises(exception=TypeError)),
         pytest.param(0.0, marks=pytest.mark.raises(exception=ValueError)),
         pytest.param('string', marks=pytest.mark.raises(exception=ValueError)),
         pytest.param({}, marks=pytest.mark.raises(exception=ValueError))
         ]
    )
    def test_init(self, oil):
        if oil is not None:
            oil_est = OilEstimation(oil)
        else:
            oil_est = OilEstimation()

        assert oil_est._k_v2 is None

    @pytest.mark.parametrize(
        'oil',
        [{'name': 'Oil Name'},
         {'oil_name': 'Oil Name'},
         ]
    )
    def test_repr(self, oil):
        oil_est = OilEstimation(oil)

        assert repr(oil_est) == '<OilEstimation(Oil Name)>'

    @pytest.mark.parametrize(
        'oil',
        [{'name': 'Oil Name',
          'temperature': {'value': 293.0, 'unit': 'K',
                          'unit_type': 'Temperature'
                          }
          },
         ]
    )
    def test_float_units(self, oil):
        oil_est = OilEstimation(oil)

        assert isinstance(oil_est.record.temperature, TemperatureUnit)

    @pytest.mark.parametrize(
        'oil',
        [{'name': 'Oil Name',
          'some_temp': 293.0
          },
         ]
    )
    def test_getattr(self, oil):
        oil_est = OilEstimation(oil)

        assert hasattr(oil_est, 'some_temp')

    @pytest.mark.parametrize(
        'oil, sample_id, product_type, expected',
        [
         ({'name': 'Oil Name'}, None, None, None),
         ({'name': 'Oil Name', 'samples': None}, None, None, None),
         ({'name': 'Oil Name', 'samples': {}}, None, None, None),
         ({'name': 'Oil Name',
           'samples': [{'name': 'Fresh Oil Sample'}]},
          '10% Weathered', None, None),
         ({'name': 'Oil Name',
           'samples': [{'name': 'Fresh Oil Sample'}]},
          None, None, {'name': 'Fresh Oil Sample'}),
         ({'name': 'Oil Name',
           'samples': [{'name': 'Fresh Oil Sample'}]},
          'Fresh Oil Sample', None, {'name': 'Fresh Oil Sample'}),
         ({'name': 'Oil Name',
           'samples': [{'name': '10% Weathered'}]},
          '10% Weathered', None, {'name': '10% Weathered'}),
         ]
    )
    def test_get_sample(self, oil, sample_id, product_type, expected):
        oil_est = OilEstimation(oil)

        if expected is not None:
            expected = OilSampleEstimation(ObjFromDict(expected), product_type)

        if sample_id is None:
            print('get_sample(): ', oil_est.get_sample())
        else:
            print('get_sample(): ', oil_est.get_sample(sample_id))

        print('expected: ', expected)

        if sample_id is None:
            assert oil_est.get_sample() == expected
        else:
            assert oil_est.get_sample(sample_id) == expected

    @pytest.mark.parametrize(
        'oil, product_type, expected',
        [
         ({'name': 'Oil Name'}, None, None),
         ({'name': 'Oil Name', 'samples': None}, None, None),
         ({'name': 'Oil Name', 'samples': {}}, None, None),
         ({'name': 'Oil Name',
           'samples': [{'sample_id': 'w=0.0'}]},
          None, {'sample_id': 'w=0.0'}),
         ]
    )
    def test_get_first_sample(self, oil, product_type, expected):
        oil_est = OilEstimation(oil)

        if expected is not None:
            expected = OilSampleEstimation(ObjFromDict(expected), product_type)

        print('get_first_sample(): ', oil_est.get_first_sample())

        print('expected: ', expected)

        assert oil_est.get_first_sample() == expected


class TestOilEstimationTemperature():
    @pytest.mark.parametrize(
        'obj_list, expected',
        [
         ([], None),
         ([{}], None),
         ([{'ref_temp': {'value': 10.0}}], {'ref_temp': {'value': 10.0}}),
         ]
    )
    def test_lowest_temperature(self, obj_list, expected):
        if obj_list is not None:
            obj_list = [ObjFromDict(o) for o in obj_list]

        if expected is not None:
            expected = ObjFromDict(expected)

        assert OilSampleEstimation.lowest_temperature(obj_list) == expected

    @pytest.mark.parametrize(
        'obj_list, temperature, expected',
        [
         ([], None, []),
         pytest.param([{}], None, [],
                      marks=pytest.mark.raises(exception=AttributeError)),
         ([{'ref_temp': {'value': 10.0, 'unit': 'C',
                         'unit_type': 'Temperature'}}
           ],
          20.0, [{'ref_temp': {'value': 10.0, 'unit': 'C',
                               'unit_type': 'Temperature'}}]
          ),
         ([
           {'ref_temp': {'value': 280.0, 'unit': 'K',
                         'unit_type': 'Temperature'}},
           {'ref_temp': {'value': 290.0, 'unit': 'K',
                         'unit_type': 'Temperature'}},
           ],
          285.0, [{'ref_temp': {'value': 280.0, 'unit': 'K',
                                'unit_type': 'Temperature'}}]
          ),
         ([
           {'ref_temp': {'value': 280.0, 'unit': 'K',
                         'unit_type': 'Temperature'}},
           {'ref_temp': {'value': 290.0, 'unit': 'K',
                         'unit_type': 'Temperature'}},
           ],
          285.01, [{'ref_temp': {
                        'value': 290.0, 'unit': 'K',
                        'unit_type': 'Temperature'}}]
          ),
         ([
           {'ref_temp': {'value': 280.0, 'unit': 'K',
                         'unit_type': 'Temperature'}},
           {'ref_temp': {'value': 290.0, 'unit': 'K',
                         'unit_type': 'Temperature'}},
           ],
          [285.0, 285.01],
          [
           [{'ref_temp': {'value': 280.0, 'unit': 'K',
                          'unit_type': 'Temperature'}}],
           [{'ref_temp': {'value': 290.0, 'unit': 'K',
                          'unit_type': 'Temperature'}}],
           ]
          ),
         ]
    )
    def test_closest_to_temperature(self, obj_list, temperature, expected):
        oil_est = OilEstimation({'name': 'Oil Name'})

        if obj_list is not None:
            obj_list = [ObjFromDict(oil_est._add_float_units(o))
                        for o in obj_list]
        print('obj_list: ', [o.__dict__ for o in obj_list])

        if expected is not None:
            if any([isinstance(o, (tuple, list, set, frozenset))
                    for o in expected]):
                expected = [[ObjFromDict(oil_est._add_float_units(o))
                             for o in i]
                            for i in expected]
            else:
                expected = [ObjFromDict(oil_est._add_float_units(o))
                            for o in expected]

            try:
                print('expected: ', [o.__dict__ for o in expected])
            except AttributeError:
                print('expected: ', [[o.__dict__ for o in i]
                                     for i in expected])

        res = OilSampleEstimation.closest_to_temperature(obj_list, temperature)

        try:
            print('results: ', [o.__dict__ for o in res])
        except AttributeError:
            print('results: ', [[o.__dict__ for o in ri] for ri in res])

        assert res == expected

    @pytest.mark.parametrize(
        'obj_list, temperature, expected',
        [
         ([], None, []),
         pytest.param([{}], None, [],
                      marks=pytest.mark.raises(exception=AttributeError)),
         ([{'ref_temp': {'value': 10.0,
                         'unit': 'C',
                         'unit_type': 'Temperature'}}
           ],
          20.0, [[
                  {'ref_temp': {'value': 10.0,
                                'unit': 'C',
                                'unit_type': 'Temperature'}},
                  {'ref_temp': {'value': 10.0,
                                'unit': 'C',
                                'unit_type': 'Temperature'}},
                 ]]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         'unit_type': 'Temperature'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         'unit_type': 'Temperature'}},
           ],
          285.0,
          [[
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            ]]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         'unit_type': 'Temperature'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         'unit_type': 'Temperature'}},
           ],
          285.01,
          [[
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            ]]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         'unit_type': 'Temperature'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         'unit_type': 'Temperature'}},
           ],
          [285.0, 285.01],
          [
           [
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            ],
           [
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          'unit_type': 'Temperature'}},
            ],
           ]
          ),
         ]
    )
    def test_bounding_temperatures(self, obj_list, temperature, expected):
        oil_est = OilEstimation({'name': 'Oil Name'})

        if obj_list is not None:
            obj_list = [ObjFromDict(oil_est._add_float_units(o))
                        for o in obj_list]

        if expected is not None:
            if any([isinstance(o, (tuple, list, set, frozenset))
                    for o in expected]):
                expected = [tuple(ObjFromDict(oil_est._add_float_units(o))
                                  for o in i)
                            for i in expected]
            else:
                expected = [ObjFromDict(oil_est._add_float_units(o))
                            for o in expected]

        res = OilSampleEstimation.bounding_temperatures(obj_list, temperature)
        assert res == expected


class TestOilEstimationPointTemperatures():
    @pytest.mark.parametrize(
        'oil, sample_id, estimate, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None, None, (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has no pour point, but has dvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'dvis': [
                   {'viscosity': {
                        'value': 0.023, 'unit': 'kg/(m s)',
                        'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 288.0, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          None, None, (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a single pour point attribute',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'pour_points': [{
                   'ref_temp': {'value': 265.0,
                                'unit': 'K',
                                'unit_type': 'Temperature'}
               }],
               'kvis': None,
           }]
           },
          None, None, (265.0, 265.0)),
         ({'name': 'Oil Name',
           'comments': 'This record has no pour point, but has kvis & dvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'dvis': [
                   {'viscosity': {
                        'value': 0.023, 'unit': 'kg/(m s)',
                        'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 288.0, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
               'kvis': [
                   {'viscosity': {
                        'value': 0.0001333, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 311.0, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          None, None, (None, 200.0)),
         ({'name': 'Oil Name',
           'comments': 'This record has no pour point, but has kvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'kvis': [
                   {'viscosity': {
                        'value': 0.0001333, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 311.0, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          None, None, (None, 200.0)),
         ({'name': 'Oil Name',
           'comments': ('This record has no pour point, '
                        'but has dvis and density'),
           'samples': [{
               'name': 'Fresh Oil Sample',
               'dvis': [
                   {'viscosity': {
                        'value': 0.3851, 'unit': 'kg/(m s)',
                        'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 288.0, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
               'densities': [
                   {'density': {
                       'value': 800.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.0, 'unit': 'K',
                        'unit_type': 'Temperature'},
                    }
               ]
           }]
           },
          None, None, (None, 200.0)),
         ]
    )
    def test_pour_point(self, oil, sample_id, estimate, expected):
        print('oil: ', oil)
        print('sample: ', sample_id)
        oil_est = OilEstimation(oil)

        if sample_id is None and estimate is None:
            res = oil_est.get_sample().pour_point()
        elif sample_id is None:
            res = oil_est.get_sample().pour_point(estimate_if_none=estimate)
        elif estimate is None:
            res = oil_est.get_sample(sample_id=sample_id).pour_point()
        else:
            res = (oil_est.get_sample(sample_id=sample_id)
                   .pour_point(estimate_if_none=estimate))

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.isclose(a, b)
            else:
                assert a == b

    @pytest.mark.parametrize(
        'oil, sample_id, estimate, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None, None, (None, None)),
         ({'name': 'Oil Name',
           'comments': ('This record has no flash point, '
                        'but has cuts & sara fractions'),
           'samples': [{
               'name': 'Fresh Oil Sample',
               'cuts': [
                   {'fraction': {
                       'value': 0.35, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 531.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.4, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 543.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.45, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 559.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
               'sara_total_fractions': [
                   {'fraction': {
                       'value': 0.895, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'sara_type': 'Saturates'},
                   {'fraction': {
                       'value': 0.093, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'sara_type': 'Aromatics'},
                   {'fraction': {
                       'value': 0.0, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'sara_type': 'Resins'},
                   {'fraction': {
                       'value': 0.01, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'sara_type': 'Asphaltenes'}
               ],


           }]
           },
          None, None, (424.41, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has no flash point, but has api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          None, None, (423.6, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a flash point',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'flash_points': [
                   {'ref_temp': {
                       'value': 273.15, 'unit': 'K',
                       'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          None, None, (273.15, 273.15)),
         ]
    )
    def test_flash_point(self, oil, sample_id, estimate, expected):
        print('oil: ', oil)
        print('sample: ', sample_id)
        oil_est = OilEstimation(oil)

        if sample_id is None and estimate is None:
            res = oil_est.get_sample().flash_point()
        elif sample_id is None:
            res = oil_est.get_sample().flash_point(estimate_if_none=estimate)
        elif estimate is None:
            res = oil_est.get_sample(sample_id=sample_id).flash_point()
        else:
            res = (oil_est.get_sample(sample_id=sample_id)
                   .flash_point(estimate_if_none=estimate))

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.isclose(a, b)
            else:
                assert a == b


class TestOilEstimationDensities():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None),
         ({'name': 'Oil Name',
           'comments': 'This record has one api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          {'gravity': 10.0}),
         ({'name': 'Oil Name',
           'comments': 'This record has multiple api gravities',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0},
                        {'gravity': 20.0},
                        {'gravity': 30.0}]
           }]
           },
          {'gravity': 10.0}),
         ({'name': 'Oil Name',
           'comments': 'This record has no api gravity, but has density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 894.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'density': {
                       'value': 89.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          None),
         ]
    )
    def test_get_api(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        res = oil_est.get_sample().get_api()

        if expected is not None:
            expected = ObjFromDict(expected)

        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None),
         ({'name': 'Oil Name',
           'comments': 'This record has one api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          10.0),
         ({'name': 'Oil Name',
           'comments': 'This record has multiple api gravities',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [
                   {'gravity': 10.0},
                   {'gravity': 20.0},
                   {'gravity': 30.0}
               ],
           }]
           },
          10.0),
         ({'name': 'Oil Name',
           'comments': 'This record has no api gravity, but has density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 994.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          10.0),
         ]
    )
    def test_get_api_from_densities(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        res = oil_est.get_sample().get_api_from_densities()

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has one api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          [
           {'density': {'value': 1000.0, 'unit': 'kg/m^3',
                        'unit_type': 'Density'},
            'ref_temp': {'value': 288.15, 'unit': 'K',
                         'unit_type': 'Temperature'}
            }
           ]),
         ({'name': 'Oil Name',
           'comments': 'This record has multiple api gravities',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [
                   {'gravity': 10.0},
                   {'gravity': 20.0},
                   {'gravity': 30.0}
               ],
           }]
           },
          [
           {'density': {'value': 1000.0, 'unit': 'kg/m^3',
                        'unit_type': 'Density'},
            'ref_temp': {'value': 288.15, 'unit': 'K',
                         'unit_type': 'Temperature'}
            }
           ]),
         ({'name': 'Oil Name',
           'comments': 'This record has no api gravity, but has density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 994.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          [
           {'density': {'value': 994.0, 'unit': 'kg/m^3',
                        'unit_type': 'Density'},
            'ref_temp': {'value': 273.15, 'unit': 'K',
                         'unit_type': 'Temperature'}
            },
           {'density': {'value': 1000.0, 'unit': 'kg/m^3',
                        'unit_type': 'Density'},
            'ref_temp': {'value': 288.15, 'unit': 'K',
                         'unit_type': 'Temperature'}
            }
           ]),
         ]
    )
    def test_get_densities(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        res = oil_est.get_sample().get_densities()

        if expected is not None:
            expected = [ObjFromDict(oil_est._add_float_units(i))
                        for i in expected]

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, temp_k, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None, None),
         ({'name': 'Oil Name',
           'comments': 'This record has one api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          None, 1000.0),
         ({'name': 'Oil Name',
           'comments': 'This record has multiple api gravities',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [
                   {'gravity': 10.0},
                   {'gravity': 20.0},
                   {'gravity': 30.0}
               ],
           }]
           },
          None, 1000.0),
         ({'name': 'Oil Name',
           'comments': 'This record has no api gravity, but has density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 994.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          None, 1000.0),
         ({'name': 'Oil Name',
           'comments': 'This record has no api gravity, but has density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 994.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          273.15, 994.0),
         ]
    )
    def test_density_at_temp(self, oil, temp_k, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        if temp_k is None:
            res = sample.density_at_temp()
        else:
            res = sample.density_at_temp(temperature=temp_k)

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None),
         ({'name': 'Oil Name',
           'comments': 'This record has one api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          1000.0),
         ({'name': 'Oil Name',
           'comments': 'This record has multiple api gravities',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [
                   {'gravity': 10.0},
                   {'gravity': 20.0},
                   {'gravity': 30.0}
               ],
           }]
           },
          1000.0),
         ({'name': 'Oil Name',
           'comments': 'This record has no api gravity, but has density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 994.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    }
               ],
           }]
           },
          1000.0),
         ]
    )
    def test_standard_density(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.standard_density

        print(res, expected)
        assert res == expected


class TestOilEstimationDynamicViscosities():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has just dvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'dvis': [
                   {'viscosity': {
                       'value': 0.025, 'unit': 'kg/(m s)',
                       'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 273.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [
           {'viscosity': {
               'value': 0.025, 'unit': 'kg/(m s)',
               'unit_type': 'Dynamic Viscosity'},
            'ref_temp': {
               'value': 273.0, 'unit': 'K',
               'unit_type': 'Temperature'}
            },
           ]),
         ({'name': 'Oil Name',
           'comments': 'This record has 1 kvis and 1 redundant dvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'kvis': [
                   {'viscosity': {
                        'value': 0.0001333, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
               'dvis': [
                   {'viscosity': {
                       'value': 0.025, 'unit': 'kg/(m s)',
                       'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': ('This record has 1 kvis '
                        'and 1 barely non-redundant dvis'),
           'samples': [{
               'name': 'Fresh Oil Sample',
               'kvis': [
                   {'viscosity': {
                        'value': 0.0001333, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
               'dvis': [
                   {'viscosity': {
                       'value': 0.025, 'unit': 'kg/(m s)',
                       'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 273.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [
           {'viscosity': {
               'value': 0.025, 'unit': 'kg/(m s)',
               'unit_type': 'Dynamic Viscosity'},
            'ref_temp': {
               'value': 273.0, 'unit': 'K',
               'unit_type': 'Temperature'}
            },
           ]),
         ]
    )
    def test_non_redundant_dvis(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = list(sample.non_redundant_dvis())

        if expected is not None:
            expected = [ObjFromDict(oil_est._add_float_units(i))
                        for i in expected]

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, kg_ms, temp_k, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None, None, None),
         ({'name': 'Oil Name',
           'comments': 'This record has only density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          None, None, None),
         ({'name': 'Oil Name',
           'comments': 'This record has only density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          1000.0, None, None),
         ({'name': 'Oil Name',
           'comments': 'This record has only density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          None, 273.15, None),
         ({'name': 'Oil Name',
           'comments': 'This record has only density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          1000.0, 273.15, 1.0),
         ]
    )
    def test_dvis_to_kvis(self, oil, kg_ms, temp_k, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.dvis_to_kvis(kg_ms, temp_k)

        print(res, expected)
        assert res == expected


class TestOilEstimationKinematicViscosities():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has only kvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'kvis': [
                   {'viscosity': {
                        'value': 1.0, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          [
           {'viscosity': {
                'value': 1.0, 'unit': 'm^2/s',
                'unit_type': 'Kinematic Viscosity'},
            'ref_temp': {
                'value': 273.15, 'unit': 'K',
                'unit_type': 'Temperature'}
            },
           ]),
         ({'name': 'Oil Name',
           'comments': 'This record has only dvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'dvis': [
                   {'viscosity': {
                       'value': 1000.0, 'unit': 'kg/(m s)',
                       'unit_type': 'Dynamic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          []),
         ]
    )
    def test_aggregate_kvis(self, oil, expected):
        print('oil: ', oil)
        print('expecting: ', expected)

        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.aggregate_kvis()

        if expected is not None:
            expected = [ObjFromDict(oil_est._add_float_units(i))
                        for i in expected]

        assert res == expected

    @pytest.mark.parametrize(
        'oil, temp_k, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None, None),
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          273.15, None),
         ({'name': 'Oil Name',
           'comments': 'This record has one kvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'kvis': [
                   {'viscosity': {
                        'value': 1.0, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          None, None),
         ({'name': 'Oil Name',
           'comments': 'This record has one kvis',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'kvis': [
                   {'viscosity': {
                        'value': 1.0, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 273.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          273.15, 1.0),
         ]
    )
    def test_kvis_at_temp(self, oil, temp_k, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        if temp_k is None:
            res = sample.density_at_temp()
        else:
            res = sample.kvis_at_temp(temp_k=temp_k)

        print(res, expected)
        assert res == expected


class TestOilEstimationDistillationFractions():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a single Resin',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          (0.1, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a single asphaltene',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          (None, 0.1)),
         ({'name': 'Oil Name',
           'comments': 'This record has a resin and an asphaltene',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          (0.1, 0.1)),
         ({'name': 'Oil Name',
           'comments': 'This record has density & viscosity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
               'kvis': [
                   {'viscosity': {
                        'value': 1.0, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          (0.277228, 0.177545)),
         ]
    )
    def test_inert_fractions(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.inert_fractions()

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.isclose(a, b)
            else:
                assert a == b

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a single Saturate',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Saturates',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          (0.1, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a single Aromatic',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Aromatics',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          (None, 0.1)),
         ({'name': 'Oil Name',
           'comments': 'This record has a Saturate and an Aromatic',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Saturates',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Aromatics',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          (0.1, 0.1)),
         ({'name': 'Oil Name',
           'comments': 'This record has density & viscosity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
               'kvis': [
                   {'viscosity': {
                        'value': 1.0, 'unit': 'm^2/s',
                        'unit_type': 'Kinematic Viscosity'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}}
               ],
           }]
           },
          (0.318597, 0.22663)),
         ]
    )
    def test_volatile_fractions(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.volatile_fractions()

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.isclose(a, b)
            else:
                assert a == b


class TestOilEstimationDistillationCuts():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          ([], [])),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          ([], [])),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          ([305.771, 384.353, 462.278, 538.126, 609.218,
            671.537, 715.374, 732.825, 735.064, 733.869],
           [0.08, 0.16, 0.24, 0.32, 0.4, 0.48, 0.56, 0.64, 0.72, 0.8])),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          ([305.771, 384.353, 462.278, 538.126, 609.218,
            671.537, 715.374, 732.825, 735.064, 733.869],
           [0.08, 0.16, 0.24, 0.32, 0.4, 0.48, 0.56, 0.64, 0.72, 0.8])),
         ]
    )
    def test_normalized_cut_values(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.normalized_cut_values()

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.allclose(a, b)
            else:
                assert a == b

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          ([], [])),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          ([], [])),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          ([305.771, 384.353, 462.278, 538.126, 609.218,
            671.537, 715.374, 732.825, 735.064, 733.869],
           [0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08])),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          ([305.771, 384.353, 462.278, 538.126, 609.218,
            671.537, 715.374, 732.825, 735.064, 733.869],
           [0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08])),
         ]
    )
    def test_get_cut_temps_fmasses(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.get_cut_temps_fmasses()

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.allclose(a, b)
            else:
                assert a == b


class TestOilEstimationComponentMethods():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          ([], [])),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          ([], [])),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          [
           305.771, 305.771, 384.353, 384.353, 462.278, 462.278,
           538.126, 538.126, 609.218, 609.218, 671.537, 671.537,
           715.374, 715.374, 732.825, 732.825, 735.064, 735.064,
           733.869, 733.869, 1015.0, 1015.0]),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [
           305.771, 305.771, 384.353, 384.353, 462.278, 462.278,
           538.126, 538.126, 609.218, 609.218, 671.537, 671.537,
           715.374, 715.374, 732.825, 732.825, 735.064, 735.064,
           733.869, 733.869, 1015.0, 1015.0]),
         ]
    )
    def test_component_temps(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.component_temps()

        print(res, expected)
        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.allclose(a, b)
            else:
                assert a == b

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          [
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Resins', 'Asphaltenes']),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Saturates', 'Aromatics', 'Saturates', 'Aromatics',
           'Resins', 'Asphaltenes']),
         ]
    )
    def test_component_types(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.component_types()

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          [70.6564, 60.6398, 106.593, 93.9145, 151.944,
           136.655, 207.924, 190.431, 274.379, 255.684,
           347.666, 329.491, 410.487, 394.411, 438.748,
           424.151, 442.525, 428.152, 440.504, 426.011,
           800.0, 1000.0]),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [70.6564, 60.6398, 106.593, 93.9145, 151.944,
           136.655, 207.924, 190.431, 274.379, 255.684,
           347.666, 329.491, 410.487, 394.411, 438.748,
           424.151, 442.525, 428.152, 440.504, 426.011,
           800.0, 1000.0]),
         ]
    )
    def test_component_mol_wt(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.component_mol_wt()

        print(res, expected)
        assert np.allclose(res, expected)

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          [682.928, 819.514, 737.032, 884.439, 783.81,
           940.572, 824.526, 989.431, 859.344, 1031.21,
           887.7, 1065.24, 906.61, 1087.93, 913.923,
           1096.71, 914.853, 1097.82, 914.357, 1097.23,
           1100.0, 1100.0]),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [682.928, 819.514, 737.032, 884.439, 783.81,
           940.572, 824.526, 989.431, 859.344, 1031.21,
           887.7, 1065.24, 906.61, 1087.93, 913.923,
           1096.71, 914.853, 1097.82, 914.357, 1097.23,
           1100.0, 1100.0]),
         ]
    )
    def test_component_densities(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.component_densities()

        print(res, expected)
        assert np.allclose(res, expected)

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          [0.683541, 0.82025, 0.737694, 0.885233, 0.784514, 0.941416,
           0.825266, 0.99032, 0.860116, 1.032139, 0.888497, 1.066197,
           0.907424, 1.08891, 0.914744, 1.097692, 0.915674, 1.098809,
           0.915178, 1.09821, 1.100988, 1.100988]),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [0.683541, 0.82025, 0.737694, 0.885233, 0.784514, 0.941416,
           0.825266, 0.99032, 0.860116, 1.032139, 0.888497, 1.066197,
           0.907424, 1.08891, 0.914744, 1.097692, 0.915674, 1.098809,
           0.915178, 1.09821, 1.100988, 1.100988]),
         ]
    )
    def test_component_specific_gravity(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.component_specific_gravity()

        print(res, expected)
        assert np.allclose(res, expected)

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has a single api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          []),
         ({'name': 'Oil Name',
           'comments': 'This record has an api and both inert fractions',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ]
           }]
           },
          [0.0728861, 0.00711392, 0.0586267, 0.0213733, 0.0417972, 0.0382028,
           0.0195837, 0.0604163,  0.0195837, 0.0604163, 0.0195837, 0.0604163,
           0.0195837, 0.0604163,  0.0195837, 0.0604163, 0.0195837, 0.0604163,
           0.0195837, 0.0604163,  0.1,       0.1]),
         ({'name': 'Oil Name',
           'comments': 'This record has distillation cuts',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'sara_total_fractions': [
                   {'sara_type': 'Resins',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
                   {'sara_type': 'Asphaltenes',
                    'fraction': {
                        'value': 10.0, 'unit': '%',
                        'unit_type': 'Float'}
                    },
               ],
               'cuts': [
                   {'fraction': {
                       'value': 0.16, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 423.6, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.48, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 738.26, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
                   {'fraction': {
                       'value': 0.8, 'unit': 'fraction',
                       'unit_type': 'Float'},
                    'vapor_temp': {
                        'value': 1052.92, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          [0.0728861, 0.00711392, 0.0586267, 0.0213733, 0.0417972, 0.0382028,
           0.0195837, 0.0604163,  0.0195837, 0.0604163, 0.0195837, 0.0604163,
           0.0195837, 0.0604163,  0.0195837, 0.0604163, 0.0195837, 0.0604163,
           0.0195837, 0.0604163,  0.1,       0.1]),
         ]
    )
    def test_component_mass_fractions(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.component_mass_fractions()

        print(res, expected)
        assert np.allclose(res, expected)


class TestOilEstimationSurfaceTensions():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has an oil-water tension',
           'samples': [{
               'name': 'Fresh Oil Sample',
               "ifts": [
                   {"interface": "water",
                    "tension": {
                       "value": 0.0275, "unit": "N/m",
                       "unit_type": "Interfacial Tension"},
                    "ref_temp": {
                        "value": 273.0, "unit": "K",
                        "unit_type": "Temperature"}
                    },
               ]
           }]
           },
          (0.0275, 273.0)),
         ({'name': 'Oil Name',
           'comments': 'This record has one api gravity',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'apis': [{'gravity': 10.0}],
           }]
           },
          (0.036429, 288.15)),
         ({'name': 'Oil Name',
           'comments': 'This record has only density',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'densities': [
                   {'density': {
                       'value': 1000.0, 'unit': 'kg/m^3',
                       'unit_type': 'Density'},
                    'ref_temp': {
                        'value': 288.15, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ],
           }]
           },
          (0.036429, 288.15)),
         ]
    )
    def test_oil_water_surface_tension(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.oil_water_surface_tension()

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has an oil-seawater tension',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'ifts': [
                   {'interface': 'seawater',
                    'tension': {
                       'value': 0.0275, 'unit': 'N/m',
                       'unit_type': 'Interfacial Tension'},
                    'ref_temp': {
                        'value': 273.0, 'unit': 'K',
                        'unit_type': 'Temperature'}
                    },
               ]
           }]
           },
          (0.0275, 273.0)),
         ]
    )
    def test_oil_seawater_surface_tension(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.oil_seawater_surface_tension()

        print(res, expected)
        assert res == expected


class TestOilEstimationEmulsion():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has no product type',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          0.0),
         ({'name': 'Oil Name',
           'product_type': 'Crude',
           'comments': 'This record is crude',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          0.9),
         ({'name': 'Oil Name',
           'product_type': 'Refined',
           'comments': 'This record is crude',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          0.0),
         ]
    )
    def test_max_water_fraction_emulsion(self, oil, expected):
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.max_water_fraction_emulsion()

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          None),
         ({'name': 'Oil Name',
           'product_type': 'Refined',
           'comments': 'This record has a refined type',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          1.0),
         ]
    )
    def test_bullwinkle_fraction(self, oil, expected):
        '''
            TODO: We need emuls_constant_max to calculate the old Adios
                  bullwinkle fraction, but it is not clear how to map this
                  information to our emulsion object.
                  So for now, we will need to leave the Adios condition out.
        '''
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.bullwinkle_fraction()

        print(res, expected)
        assert res == expected


class TestOilEstimationMisc():
    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          0.0),
         ]
    )
    def test_solubility(self, oil, expected):
        '''
            This function basically returns a constant, so not much to test.
        '''
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.solubility()

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          0.035),
         ({'name': 'Oil Name',
           'comments': 'This record has an adhesion',
           'samples': [{
               'name': 'Fresh Oil Sample',
               'adhesions': [
                   {'adhesion': {
                       'value': 0.28, 'unit': 'N/m^2',
                       'unit_type': 'Pressure'}
                    },
               ],
           }]
           },
          0.28),
         ]
    )
    def test_adhesion(self, oil, expected):
        '''
            This function basically returns a constant, so not much to test.
        '''
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.adhesion()

        print(res, expected)
        assert res == expected

    @pytest.mark.parametrize(
        'oil, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'name': 'Fresh Oil Sample',
           }]
           },
          0.0),
         ({'name': 'Oil Name',
           'comments': 'This record has a single sulfur',
           'samples': [{
               'name': 'Fresh Oil Sample',
               "sulfur": [
                   {"fraction": {
                       "value": 0.0015, "unit": "fraction",
                       "unit_type": "Float"}
                    }
               ],
           }]
           },
          0.0015),
         ]
    )
    def test_sulfur_fraction(self, oil, expected):
        '''
            This function basically returns a constant, so not much to test.
        '''
        print('oil: ', oil)
        oil_est = OilEstimation(oil)

        sample = oil_est.get_sample()

        res = sample.sulphur_fraction()

        print(res, expected)
        assert res == expected
