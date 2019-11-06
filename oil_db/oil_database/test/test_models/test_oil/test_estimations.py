'''
    Test our Oil Model Estimations class
'''
import pytest

import numpy as np

from oil_database.util.json import ObjFromDict
from oil_database.data_sources.oil.estimations import OilEstimation
from oil_database.models.common.float_unit import TemperatureUnit


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
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'
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
        'oil, sample_id, expected',
        [
         ({'name': 'Oil Name'}, None, None),
         ({'name': 'Oil Name', 'samples': None}, None, None),
         ({'name': 'Oil Name', 'samples': {}}, None, None),
         ({'name': 'Oil Name',
           'samples': [{'sample_id': 'w=0.0'}]},
          'w=1.0', None),
         ({'name': 'Oil Name',
           'samples': [{'sample_id': 'w=0.0'}]},
          None, {'sample_id': 'w=0.0'}),
         ({'name': 'Oil Name',
           'samples': [{'sample_id': 'w=0.0'}]},
          'w=0.0', {'sample_id': 'w=0.0'}),
         ({'name': 'Oil Name',
           'samples': [{'sample_id': 'w=1.0'}]},
          'w=1.0', {'sample_id': 'w=1.0'}),
         ]
    )
    def test_get_sample(self, oil, sample_id, expected):
        oil_est = OilEstimation(oil)

        if expected is not None:
            expected = ObjFromDict(expected)

        if sample_id is None:
            assert oil_est.get_sample() == expected
        else:
            assert oil_est.get_sample(sample_id) == expected


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

        assert OilEstimation.lowest_temperature(obj_list) == expected

    @pytest.mark.parametrize(
        'obj_list, temperature, expected',
        [
         ([], None, []),
         pytest.param([{}], None, [],
                      marks=pytest.mark.raises(exception=AttributeError)),
         ([{'ref_temp': {'value': 10.0,
                         'unit': 'C',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}}
           ],
          20.0, [{'ref_temp': {'value': 10.0,
                               'unit': 'C',
                               '_cls': 'oil_database.models.common.float_unit'
                                       '.TemperatureUnit'}}]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           ],
          285.0, [{'ref_temp': {'value': 280.0,
                                'unit': 'K',
                                '_cls': 'oil_database.models.common.float_unit'
                                        '.TemperatureUnit'}}]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           ],
          285.01, [{'ref_temp': {'value': 290.0,
                                 'unit': 'K',
                                 '_cls': 'oil_database.models.common.float_unit'
                                         '.TemperatureUnit'}}]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           ],
          [285.0, 285.01],
          [
           [{'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}}],
           [{'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}}],
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

        res = OilEstimation.closest_to_temperature(obj_list, temperature)

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
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}}
           ],
          20.0, [[
                  {'ref_temp': {'value': 10.0,
                                'unit': 'C',
                                '_cls': 'oil_database.models.common.float_unit'
                                        '.TemperatureUnit'}},
                  {'ref_temp': {'value': 10.0,
                                'unit': 'C',
                                '_cls': 'oil_database.models.common.float_unit'
                                        '.TemperatureUnit'}},
                 ]]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           ],
          285.0,
          [[
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            ]]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           ],
          285.01,
          [[
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            ]]
          ),
         ([
           {'ref_temp': {'value': 280.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           {'ref_temp': {'value': 290.0,
                         'unit': 'K',
                         '_cls': 'oil_database.models.common.float_unit'
                                 '.TemperatureUnit'}},
           ],
          [285.0, 285.01],
          [
           [
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            ],
           [
            {'ref_temp': {'value': 280.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
            {'ref_temp': {'value': 290.0,
                          'unit': 'K',
                          '_cls': 'oil_database.models.common.float_unit'
                                  '.TemperatureUnit'}},
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

        res = OilEstimation.bounding_temperatures(obj_list, temperature)
        assert res == expected


class TestOilEstimationPointTemperatures():
    @pytest.mark.parametrize(
        'oil, sample, estimate, expected',
        [
         ({'name': 'Oil Name',
           'comments': 'This record has an empty sample',
           'samples': [{
               'sample_id': 'w=0.0',
           }]
           },
          None, None, (None, None)),
         ({'name': 'Oil Name',
           'comments': 'This record has a single pour point attribute',
           'samples': [{
               'sample_id': 'w=0.0',
               'pour_points': [{
                   'ref_temp': {'value': 265.0,
                                'unit': 'K',
                                '_cls': 'oil_database.models.common.float_unit'
                                        '.TemperatureUnit'}
               }],
               'kvis': None,
           }]
           },
          None, None, (265.0, 265.0)),
         ({'name': 'Oil Name',
           'comments': 'This record has no pour point, but has kvis & dvis',
           'samples': [{
               'sample_id': 'w=0.0',
               'dvis': [
                   {'viscosity': {
                        'value': 0.023, 'unit': 'kg/(m s)',
                        '_cls': 'oil_database.models.common.float_unit'
                                '.DynamicViscosityUnit'},
                    'ref_temp': {
                        'value': 288.0, 'unit': 'K',
                        '_cls': 'oil_database.models.common.float_unit'
                                '.TemperatureUnit'}}
               ],
               'kvis': [
                   {'viscosity': {
                        'value': 0.0000424, 'unit': 'm^2/s',
                        '_cls': 'oil_database.models.common.float_unit'
                                '.KinematicViscosityUnit'},
                    'ref_temp': {
                        'value': 311.0, 'unit': 'K',
                        '_cls': 'oil_database.models.common.float_unit'
                                '.TemperatureUnit'}}
               ],
           }]
           },
          None, None, (265.0, 265.0)),
         ({'name': 'Oil Name',
           'comments': 'This record has no pour point, but has kvis',
           'samples': [{
               'sample_id': 'w=0.0',
               'kvis': [
                   {'viscosity': {
                        'value': 0.000134, 'unit': 'm^2/s',
                        '_cls': 'oil_database.models.common.float_unit'
                                '.KinematicViscosityUnit'},
                    'ref_temp': {
                        'value': 311.0, 'unit': 'K',
                        '_cls': 'oil_database.models.common.float_unit'
                                '.TemperatureUnit'}}
               ],
           }]
           },
          None, None, (None, 200.0)),
         ]
    )
    def test_pour_point(self, oil, sample, estimate, expected):
        oil_est = OilEstimation(oil)

        if sample is None and estimate is None:
            res = oil_est.pour_point()
        elif sample is None:
            res = oil_est.pour_point(estimate_if_none=estimate)
        elif estimate is None:
            res = oil_est.pour_point(sample=sample)
        else:
            res = oil_est.pour_point(sample=sample, estimate_if_none=estimate)

        for a, b in zip(res, expected):
            if a is not None and b is not None:
                assert np.isclose(a, b)
            else:
                assert a == b






















