import pytest

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.completeness import completeness, MAX_SCORE


## Fixme! We should not be using JSON for testing (except for testing JSON read/writing)
##        It makes all the tests very sensitive to changes!
##

# xfail = pytest.mark.xfail(True, reason="subamples need metadata")

class TestAllCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'This should have everything.  100% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'densities': [
                          {
                              'density': {'value': 1000, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 10, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'density': {'value': 950, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 30, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                      ],
                      'dynamic_viscosities': [
                          {
                              'viscosity': {'value': 1300, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 0.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                          {
                              'viscosity': {'value': 1500, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 20.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                      ],
                  },
                  'environmental_behavior': {'emulsions': [
                      {
                          'age': {"value": 0, "unit": "day",
                                  "unit_type": "time"},
                          'water_content': {'value': 10, 'unit': '%',
                                            'unit_type': 'massfraction'}
                      }
                  ]},
                  'distillation_data': {'cuts': [
                          {
                            'fraction': {'value': 0, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 56, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 100, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 84, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                  ]}
              },
              {
                  'metadata': {'fraction_evaporated': {'value': 0.15, 'unit': 'fraction',
                                                       'unit_type': 'MassFraction'}},
                  'physical_properties': {
                      'densities': [
                          {
                              'density': {'value': 15, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 10, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                      ],
                      'dynamic_viscosities': [
                          {
                              'viscosity': {'value': 1500, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 0.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                      ],
                  },
              },
          ]
          },
         100),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert completeness(oil) == round(expected / MAX_SCORE * 10)

class TestDistillationCompleteness:

    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just distillation, 2 cuts.  30% score'},
          'sub_samples': [
              {
                  'distillation_data': {'cuts': [
                          {
                            'fraction': {'value': 0, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 56, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 100, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 84, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                  ]}
              },
          ]
          },
         30),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just distillation, 2 cuts, '
                                  'partial fraction range.  15% score'},
          'sub_samples': [
              {
                  'distillation_data': {'cuts': [
                          {
                            'fraction': {'value': 0, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 56, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 50, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 84, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                  ]}
              },
          ]
          },
         15),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert completeness(oil) == round(expected / MAX_SCORE * 10)

        # add fraction_recovered
        # less than one adds 1 point
        oil.sub_samples[0].distillation_data.fraction_recovered = 0.8
        assert completeness(oil) == round((expected + 10) / MAX_SCORE * 10)

        # exactly one adds 2 points
        oil.sub_samples[0].distillation_data.fraction_recovered = 1.0
        assert completeness(oil) == round((expected + 20) / MAX_SCORE * 10)


class TestViscosityCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just one viscosity. 5% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'dynamic_viscosities': [
                          {
                              'viscosity': {'value': 1300, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 0.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                      ],
                  },
              },
          ]
          },
         5),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Second viscosity. 10% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'dynamic_viscosities': [
                          {
                              'viscosity': {'value': 1300, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 0.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                          {
                              'viscosity': {'value': 1500, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 20.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                      ],
                  },
              },
          ]
          },
         10),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Second viscosity, '
                                  'partial temperature range. 8% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'dynamic_viscosities': [
                          {
                              'viscosity': {'value': 1300, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 0.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                          {
                              'viscosity': {'value': 1500, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 10.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                      ],
                  },
              },
          ]
          },
         8),
        ({'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just one weathered viscosity.  10% score'},
          'sub_samples': [
              {
              },
              {
                  'metadata': {'fraction_evaporated': {'value': 0.15, 'unit': 'fraction',
                                                       'unit_type': 'MassFraction'}},
                  'physical_properties': {
                      'dynamic_viscosities': [
                          {
                              'viscosity': {'value': 1500, 'unit': 'mPa.s',
                                            'unit_type': 'dynamicviscosity'},
                              'ref_temp': {'value': 0.0, 'unit': 'C',
                                           'unit_type': 'temperature'},
                          },
                      ],
                  },
              },
          ]
          },
         10),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert completeness(oil) == round(expected / MAX_SCORE * 10)


class TestDensityCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just one density.  10% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'densities': [
                          {
                              'density': {'value': 1000, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 10, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                      ],
                  },
              },
          ]
          },
         10),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Second density.  15% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'densities': [
                          {
                              'density': {'value': 1000, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 10, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'density': {'value': 950, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 30, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                      ],
                  },
              },
          ]
          },
         15),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Second density, '
                                  'partial temperature range. 12.5% score'},
          'sub_samples': [
              {
                  'physical_properties': {
                      'densities': [
                          {
                              'density': {'value': 1000, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 10, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'density': {'value': 950, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 20, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                      ],
                  },
              },
          ]
          },
         12.5),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just weathered density.  10% score'},
          'sub_samples': [
              {
              },
              {
                      'metadata': {'fraction_evaporated': {'value': 0.15, 'unit': 'fraction',
                                                           'unit_type': 'MassFraction'}},
                      'physical_properties': {
                      'densities': [
                          {
                              'density': {'value': 1000, 'unit': 'kg/m^3',
                                          'unit_type': 'density'},
                              'ref_temp': {'value': 10, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                      ],
                  },
              },
          ]
          },
         10),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert completeness(oil) == round(expected / MAX_SCORE * 10)


class TestEmulsionCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just emulsion.  25% score'},
          'sub_samples': [
              {
                  'environmental_behavior': {'emulsions': [
                      {
                          'age': {"value": 0, "unit": "day",
                                  "unit_type": "time"},
                          'water_content': {'value': 10, 'unit': '%',
                                            'unit_type': 'massfraction'}
                      }
                  ]},
              },
          ]
          },
         25),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'weathered sample emulsion.  25% score'},
          'sub_samples': [
              {
              },
              {
                  'environmental_behavior': {'emulsions': [
                      {
                          'age': {"value": 0, "unit": "day",
                                  "unit_type": "time"},
                          'water_content': {'value': 10, 'unit': '%',
                                            'unit_type': 'massfraction'}
                      }
                  ]},
              },
          ]
          },
         25),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert completeness(oil) == round(expected / MAX_SCORE * 10)

