import pytest

from oil_database.models.oil.completeness import completeness


class TestAllCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999',
          'metadata': {'comment': 'This should have everything.  100% score'},
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
                      {'value': 10, 'unit': '%', 'unit_type': 'massfraction'}
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
        assert completeness(oil_json) == expected


class TestDistillationCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just distillation, 2 cuts.  30% score'},
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
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just distillation, 2 cuts, '
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
        assert completeness(oil_json) == expected


class TestViscosityCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just one viscosity. 5% score'},
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
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Second viscosity. 10% score'},
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
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Second viscosity, '
                                  'partial temperature range. 7.5% score'},
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
         7.5),
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just one weathered viscosity.  10% score'},
          'sub_samples': [
              {
              },
              {
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
        assert completeness(oil_json) == expected


class TestDensityCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just one density.  10% score'},
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
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Second density.  15% score'},
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
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Second density, '
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
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just weathered density.  10% score'},
          'sub_samples': [
              {
              },
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
    ])
    def test_completeness_score(self, oil_json, expected):
        assert completeness(oil_json) == expected


class TestEmulsionCompleteness:
    @pytest.mark.parametrize('oil_json, expected', [
        ({'_id': 'EC09999',
          'metadata': {'comment': 'Just emulsion.  25% score'},
          'sub_samples': [
              {
                  'environmental_behavior': {'emulsions': [
                      {'value': 10, 'unit': '%', 'unit_type': 'massfraction'}
                  ]},
              },
          ]
          },
         25),
        ({'_id': 'EC09999',
          'metadata': {'comment': 'weathered sample emulsion.  25% score'},
          'sub_samples': [
              {
              },
              {
                  'environmental_behavior': {'emulsions': [
                      {'value': 10, 'unit': '%', 'unit_type': 'massfraction'}
                  ]},
              },
          ]
          },
         25),
    ])
    def test_completeness_score(self, oil_json, expected):
        assert completeness(oil_json) == expected
