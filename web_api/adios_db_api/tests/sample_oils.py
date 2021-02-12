"""
    Sample oil records for testing.
"""

from adios_db.models.oil.oil import Oil


basic_noaa_fm_pyjson = {
    'metadata': {
        'API': 28.0,
        'labels': ['Crude', 'Medium'],
        'location': 'WRC',
        'name': 'BASIC NOAA FILEMAKER TEST RECORD',
        'product_type': 'crude',
        'reference': {
            'reference': 'Derived from the Abu Safah oil record',
            'year': 1993
        },
        'source_id': 'AD00009'
    },
    'oil_id': 'AD99999',
    'status': [
        'W007: No distillation data provided'
    ],
    'sub_samples': [
        {
            'distillation_data': {
                'type': 'mass'
            },
            'metadata': {
                'fraction_weathered': {
                    'unit': '1',
                    'unit_type': 'massfraction',
                    'value': 0.0
                },
                'name': 'Fresh Oil Sample',
                'short_name': 'Fresh Oil'
            },
            'physical_properties': {
                'kinematic_viscosities': [
                    {
                        'ref_temp': {
                            'unit': 'K',
                            'unit_type': 'temperature',
                            'value': 294.0
                        },
                        'viscosity': {
                            'unit': 'm^2/s',
                            'unit_type': 'kinematicviscosity',
                            'value': 2.5e-05
                        }
                    },
                    {
                        'ref_temp': {
                            'unit': 'K',
                            'unit_type': 'temperature',
                            'value': 311.0
                        },
                        'viscosity': {
                            'unit': 'm^2/s',
                            'unit_type': 'kinematicviscosity',
                            'value': 1.44e-05
                        }
                    }
                ],
                'pour_point': {
                    'measurement': {
                        'unit': 'K',
                        'unit_type': 'temperature',
                        'value': 244.0
                    }
                }
            }
        }
    ]
}

#  Round tripping through the Oil object to make sure it's consistent
basic_noaa_fm = Oil.from_py_json(basic_noaa_fm_pyjson).py_json()

