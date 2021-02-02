'''
tests for adding suggested labels to oil
'''

import pytest

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample

from adios_db.models.oil.cleanup.add_labels import get_suggested_labels

from adios_db.models.oil.physical_properties import KinematicViscosityPoint
from adios_db.models.common import measurement as meas


def add_kin_viscosity_to_oil(oil, viscosities, temp, unit, kvis_temp=15.0, temp_unit="C"):
    try:
        sample = oil.sub_samples[0]
    except IndexError:
        sample = Sample()
        sample.metadata.name = "only viscosity"
        oil.sub_samples.append(sample)
    for kvis in viscosities:
        kp = KinematicViscosityPoint(meas.KinematicViscosity(kvis, unit=unit),
                                     meas.Temperature(kvis_temp, unit=temp_unit))
        sample.physical_properties.kinematic_viscosities.append(kp)
    return None


def test_add_labels_to_oil_no_product_type():
    '''
    this oil should get no labels
    '''
    oil = Oil('XXXXX')

    assert get_suggested_labels(oil) == set()


def test_add_labels_to_oil_no_labels_other():
    '''
    we should never get a label for 'Other'
    '''
    oil = Oil('XXXXX')
    oil.metadata.API = 32.0
    oil.metadata.product_type = 'Other'

    assert get_suggested_labels(oil) == set()


@pytest.mark.parametrize('pt, api, labels', [('Crude Oil NOS', 32.0, {'Light Crude', 'Crude Oil'}),
                                             ('Crude Oil NOS', 25.0, {'Medium Crude', 'Crude Oil'}),
                                             ('Crude Oil NOS', 22.0, {'Heavy Crude', 'Crude Oil'}),
                                             ('Crude Oil NOS', 9.9, {'Heavy Crude', 'Group V', 'Crude Oil', 'Bitumen'}),
                                             ('Tight Oil', 32, {'Fracking Oil', 'Shale Oil', 'Crude Oil'}),
                                             ('Residual Fuel Oil', 13, {'Refined Product', 'Bunker C', 'Residual Fuel', 'Fuel Oil', 'HFO', 'Heavy Fuel Oil'}),
                                             ('Residual Fuel Oil', 16, {'Refined Product', 'Residual Fuel', 'Fuel Oil'}),
                                             ('Distillate Fuel Oil', 32, {'Refined Product', 'Fuel Oil', }),
                                             ]
                         )
def test_add_labels_to_oil_api(pt, api, labels):
    '''
    we should never get a label for 'Other'
    '''
    oil = Oil('XXXXX')
    oil.metadata.API = api
    oil.metadata.product_type = pt

    print("Product type:", pt)
    print("API:", api)
    print("labels:", get_suggested_labels(oil))
    assert get_suggested_labels(oil) == labels

@pytest.mark.parametrize('pt, api, kvis, kvis_temp, labels',
                         [('Distillate Fuel Oil', 32.0, 3, 38, {'Refined Product','Fuel Oil', 'No. 2 Fuel Oil','Diesel','Home Heating Oil'}),
                          ('Distillate Fuel Oil', 32.0, 6, 38, {'Refined Product', 'Fuel Oil'}),
                          ('Distillate Fuel Oil', 32.0, 1, 38, {'Refined Product', 'Fuel Oil'}),
                          # HFOs
                          ('Residual Fuel Oil', 14.0, 210, 50, {'Refined Product', 'Bunker C', 'Residual Fuel', 'Fuel Oil', 'Heavy Fuel Oil', 'HFO'}),
                          # IFOs
                          ('Residual Fuel Oil', 29.0, 5, 38, {'Refined Product', 'Residual Fuel', 'Fuel Oil', 'IFO'}),
                          ]
                         )


def test_add_labels_to_oil_api_and_visc(pt, api, kvis, kvis_temp, labels):
    '''
    refined products with density and viscosity limits
    '''
    oil = Oil('XXXXX')
    oil.metadata.API = api
    oil.metadata.product_type = pt
    add_kin_viscosity_to_oil(oil, (kvis,), 15, 'cSt', kvis_temp, 'C')

    print("Product type:", pt)
    print("API:", api)
    print("labels:", get_suggested_labels(oil))
    assert get_suggested_labels(oil) == labels
