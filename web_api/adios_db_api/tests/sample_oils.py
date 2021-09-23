"""
    Sample oil records for testing.

NOTE: Maybe better to get this directly from the adios_db test data
      (this last copied 2021-09-23)
"""
import json
from adios_db.models.oil.oil import Oil

basic_noaa_fm_json = """{
    "oil_id": "AD99999",
    "adios_data_model_version": "0.11.0",
    "metadata": {
        "name": "SEPINGGAN-YAKIN, OIL & GAS",
        "source_id": "AD01901",
        "location": "INDONESIA",
        "reference": {
            "year": 1998,
            "reference": "McNamara, J. (ed.), Patterson, M. (ed.),1998. Oil & Gas Journal Data Book. Tulsa, OK: Pennwell Books. 402 pp."
        },
        "product_type": "Crude Oil NOS",
        "API": 31.7,
        "labels": [
            "Crude Oil",
            "Light Crude"
        ],
        "model_completeness": 15,
        "gnome_suitable": true
    },
    "sub_samples": [
        {
            "metadata": {
                "name": "Fresh Oil Sample",
                "short_name": "Fresh Oil",
                "fraction_evaporated": {
                    "value": 0.0,
                    "unit": "fraction",
                    "unit_type": "massfraction"
                }
            },
            "physical_properties": {
                "pour_point": {
                    "measurement": {
                        "value": -7,
                        "unit": "C",
                        "unit_type": "temperature"
                    }
                },
                "densities": [
                    {
                        "density": {
                            "value": 866.28,
                            "unit": "kg/m^3",
                            "unit_type": "density"
                        },
                        "ref_temp": {
                            "value": 288.16,
                            "unit": "K",
                            "unit_type": "temperature"
                        },
                        "method": "Converted from API"
                    }
                ],
                "kinematic_viscosities": [
                    {
                        "viscosity": {
                            "value": 3.16e-06,
                            "unit": "m^2/s",
                            "unit_type": "kinematicviscosity"
                        },
                        "ref_temp": {
                            "value": 38,
                            "unit": "C",
                            "unit_type": "temperature"
                        }
                    }
                ]
            },
            "distillation_data": {
                "type": "mass fraction"
            },
            "bulk_composition": [
                {
                    "name": "sulfur",
                    "measurement": {
                        "value": 0.0011,
                        "unit": "fraction",
                        "unit_type": "massfraction"
                    }
                }
            ],
            "industry_properties": [
                {
                    "name": "Conradson Carbon Residue (CCR)",
                    "measurement": {
                        "value": 0.0054,
                        "unit": "fraction",
                        "unit_type": "massfraction"
                    }
                }
            ]
        }
    ],
    "review_status": {
        "status": "Not Reviewed"
    }
}
"""
#  Round tripping through the Oil object to make sure it's consistent
basic_noaa_fm = Oil.from_py_json(json.loads(basic_noaa_fm_json)).py_json()


# {
#     'oil_id': 'AD99999',
#     'adios_data_model_version': '0.11.0',
#     'metadata': {
#         'API': 28.0,
#         'labels': ['Crude Oil', 'Medium Crude'],
#         'location': 'WRC',
#         'name': 'SIMPLE NOAA TEST RECORD',
#         'product_type': 'Crude Oil NOS',
#         'reference': {
#             'reference': 'Derived from the Abu Safah oil record',
#             'year': 1993
#         },
#         'source_id': 'AD00009'
#     },
#     'status': [
#         'W007: No distillation data provided'
#     ],
#     'sub_samples': [
#         {
#             'distillation_data': {
#                 'type': 'mass'
#             },
#             'metadata': {
#                 'fraction_weathered': {
#                     'unit': '1',
#                     'unit_type': 'massfraction',
#                     'value': 0.0
#                 },
#                 'name': 'Fresh Oil Sample',
#                 'short_name': 'Fresh Oil'
#             },
#             'physical_properties': {
#                 'kinematic_viscosities': [
#                     {
#                         'ref_temp': {
#                             'unit': 'K',
#                             'unit_type': 'temperature',
#                             'value': 294.0
#                         },
#                         'viscosity': {
#                             'unit': 'm^2/s',
#                             'unit_type': 'kinematicviscosity',
#                             'value': 2.5e-05
#                         }
#                     },
#                     {
#                         'ref_temp': {
#                             'unit': 'K',
#                             'unit_type': 'temperature',
#                             'value': 311.0
#                         },
#                         'viscosity': {
#                             'unit': 'm^2/s',
#                             'unit_type': 'kinematicviscosity',
#                             'value': 1.44e-05
#                         }
#                     }
#                 ],
#                 'pour_point': {
#                     'measurement': {
#                         'unit': 'K',
#                         'unit_type': 'temperature',
#                         'value': 244.0
#                     }
#                 }
#             }
#         }
#     ]
# }


