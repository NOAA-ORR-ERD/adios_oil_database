'''
tests for adding suggested labels to oil
'''

import pytest

from adios_db.models.oil.oil import Oil

from adios_db.models.oil.cleanup.add_labels import get_suggested_labels


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
                                             ('Crude Oil NOS', 9.9, {'Heavy Crude', 'Group V', 'Crude Oil'}),
                                             ('Tight Oil', 32, {'Fracking Oil', 'Shale Oil', 'Crude Oil'}),
                                             ('Residual Fuel Oil', 13, {'Fuel Oil', 'HFO', 'Heavy Fuel Oil'}),
                                             ('Residual Fuel Oil', 16, {'Fuel Oil'}),
                                             ('Distillate Fuel Oil', 32, {'Fuel Oil', }),
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

