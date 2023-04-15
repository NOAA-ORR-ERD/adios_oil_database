import pytest

from adios_db.models.oil.oil import Oil
from adios_db.models.common.measurement import MassFraction

from adios_db.models.oil.completeness import (completeness,
                                              MAX_SCORE,
                                              CheckDistillation,
                                              CheckViscosity)


# Fixme! We should not be using JSON for testing (except for testing JSON
#        read/writing)
#        It makes all the tests very sensitive to changes!
#

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
                  'distillation_data': {
                      "fraction_recovered": {"value": 1.0,
                                             "unit": "fraction",
                                             "unit_type": "concentration"},
                      'cuts': [
                          {
                            'fraction': {'value': 10, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 100, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 20, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 150, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                          {
                            'fraction': {'value': 30, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 175, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 40, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 210, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          }]
                      }
              },
              {
                  'metadata': {
                      'fraction_evaporated': {'value': 0.15,
                                              'unit': 'fraction',
                                              'unit_type': 'MassFraction'}
                  },
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

        assert completeness(oil) == expected


class TestDistillationCompleteness:
    Dcheck = CheckDistillation()

    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just distillation, 2 cuts'},
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
         1),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just distillation, 3 cuts'},
          'sub_samples': [
              {
                  'distillation_data': {'cuts': [
                          {
                            'fraction': {'value': 0, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 100, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 20, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 150, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 30, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 200, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                  ]}
              },
          ]
          },
         2),
        ({'_id': 'EC09999', 'oil_id': 'EC09999',
          "adios_data_model_version": "0.11.0",
          'metadata': {'comments': 'Just distillation, 4 cuts'},
          'sub_samples': [
              {
                  'distillation_data': {'cuts': [
                          {
                            'fraction': {'value': 0, 'unit': '%',
                                         'unit_type': 'massfraction'},
                            'vapor_temp': {'value': 100, 'unit': 'C',
                                           'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 20, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 150, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 30, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 200, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                          {
                              'fraction': {'value': 40, 'unit': '%',
                                           'unit_type': 'massfraction'},
                              'vapor_temp': {'value': 250, 'unit': 'C',
                                             'unit_type': 'temperature'}
                          },
                  ]}
              },
          ]
          },
         3),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert self.Dcheck(oil) == expected

        dist_data = oil.sub_samples[0].distillation_data

        # add fraction_recovered
        # less than one adds 1 point
        dist_data.fraction_recovered = MassFraction(0.8, unit="fraction")
        assert self.Dcheck(oil) == expected + 2

        # exactly one adds 2 points
        dist_data.fraction_recovered = MassFraction(1.0, unit="fraction")
        assert self.Dcheck(oil) == expected + 2


just_one_viscosity = {
    '_id': 'EC09999',
    'oil_id': 'EC09999',
    "adios_data_model_version": "0.11.0",
    'metadata': {'comments': 'Just one viscosity'},
    'sub_samples': [{
        'physical_properties': {
            'dynamic_viscosities': [{
                'viscosity': {'value': 1300, 'unit': 'mPa.s',
                              'unit_type': 'dynamicviscosity'},
                'ref_temp': {'value': 0.0, 'unit': 'C',
                             'unit_type': 'temperature'},
            }]
        },
    }]
}

two_fresh_viscosities = {
    '_id': 'EC09999',
    'oil_id': 'EC09999',
    "adios_data_model_version": "0.11.0",
    'metadata': {'comments': 'Second viscosity'},
    'sub_samples': [{
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
                    'ref_temp': {'value': 15.0, 'unit': 'C',
                                 'unit_type': 'temperature'},
                },
            ],
        },
    }]
}

two_viscosities_partial_temp_range = {
    '_id': 'EC09999',
    'oil_id': 'EC09999',
    "adios_data_model_version": "0.11.0",
    'metadata': {
        'comments': 'Second viscosity, partial temperature range. 8% score'
    },
    'sub_samples': [{
        'physical_properties': {
            'kinematic_viscosities': [
                {
                    'viscosity': {'value': 1300, 'unit': 'mPa.s',
                                  'unit_type': 'kinematicviscosity'},
                    'ref_temp': {'value': 0.0, 'unit': 'C',
                                 'unit_type': 'temperature'},
                },
                {
                    'viscosity': {'value': 1500, 'unit': 'mPa.s',
                                  'unit_type': 'kinematicviscosity'},
                    'ref_temp': {'value': 10.0, 'unit': 'C',
                                 'unit_type': 'temperature'},
                },
            ],
        },
    }]
}

one_weathered_viscosity_no_fresh = {
    'oil_id': 'EC09999',
    "adios_data_model_version": "0.11.0",
    'metadata': {'comments': 'Just one weathered viscosity -- no fresh'},
    'sub_samples': [
        {},
        {
            'metadata': {
                'fraction_evaporated': {'value': 0.15, 'unit': 'fraction',
                                        'unit_type': 'MassFraction'}
            },
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
}

one_weathered_viscosity_two_fresh = {
    'oil_id': 'EC09999',
    "adios_data_model_version": "0.11.0",
    'metadata': {'comments': 'One weathered viscosity -- two fresh'},
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
        {
            'metadata': {
                'fraction_evaporated': {'value': 0.15,
                                        'unit': 'fraction',
                                        'unit_type': 'MassFraction'}
            },
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
}


class TestViscosityCompleteness:
    Vcheck = CheckViscosity()

    @pytest.mark.parametrize('oil_json, expected', [
        (just_one_viscosity, 1.0),
        (two_fresh_viscosities, 1.5),
        (two_viscosities_partial_temp_range, (1 + 10.0 / 30.0)),
        (one_weathered_viscosity_no_fresh, 0),
        (one_weathered_viscosity_two_fresh, 2.5),
    ])
    def test_completeness_score(self, oil_json, expected):
        oil = Oil.from_py_json(oil_json)
        assert self.Vcheck(oil) == expected


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
                  'metadata': {
                      'fraction_evaporated': {'value': 0.15,
                                              'unit': 'fraction',
                                              'unit_type': 'MassFraction'}
                  },
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
