"""
integrated tests for the Oil object

impossible to be comprehensive here, but at least we can make sure it works

for *some* cases.

Add more when you find bugs

NOTE: this is kind of pointless now.

"""
from adios_db.models.oil.oil import Oil


def test_make_oil_from_partial():
    # this one has stuff needed for the completeness tests, but not much else
    PARTIAL_JSON = {
        'oil_id': 'EC09999',
        'metadata': {'comments': 'A comment'},
        'sub_samples': [
              {
                  "metadata": {
                      "name": "Fresh Oil Sample",
                      "short_name": "Fresh Oil",
                      },
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
                  "metadata": {
                      "name": "Evaporated Oil Sample",
                      "short_name": "Evaporated Oil",
                      "fraction_weathered": {'value': 15, 'unit': '%',
                                             'unit_type': 'massfraction'}
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
        }

    print(PARTIAL_JSON["sub_samples"][0]['metadata'])

    oil = Oil.from_py_json(PARTIAL_JSON)

    assert oil.oil_id == 'EC09999'
    assert oil.metadata.comments == "A comment"
    assert oil.sub_samples[0].physical_properties.densities[0].density.value == 1000
    assert oil.sub_samples[0].metadata.name == "Fresh Oil Sample"
