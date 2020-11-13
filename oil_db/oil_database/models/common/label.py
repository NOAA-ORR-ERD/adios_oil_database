from dataclasses import dataclass
from ..common.utilities import dataclass_to_json
from oil_database.util.many_many import ManyMany

'''
    It has been decided that our labels will operate in a similar
    manner to a simple tagging system.  However, we want to have the
    ability to filter the labels based on the product type.  So we build an
    association table.
'''
_label_to_types = {
    'Crude Oil': ['Crude Oil NOS', 'Condensate', 'Bitumen Blend', 'Other'],
    'Bitumen Blend': ['Crude Oil NOS', 'Bitumen Blend', 'Refined Product NOS',
                      'Refinery Intermediate', 'Other'],
    'Condensate': ['Condensate', 'Other'],
    'Refined Product': ['Bitumen Blend', 'Refined Product NOS', 'Fuel Oil NOS',
                        'Distillate Fuel Oil', 'Petroleum-Derived Solvent',
                        'Residual Fuel Oil', 'Bio-fuel Oil',
                        'Bio-Petroleum Fuel Oil', 'Lube Oil',
                        'Refinery Intermediate', 'Natural Plant Oil',
                        'Dielectric Oil', 'Other'],
    'Fuel Oil': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
                 'Residual Fuel Oil', 'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil',
                 'Natural Plant Oil', 'Other'],
    'Distillate Fuel': ['Refined Product NOS', 'Fuel Oil NOS',
                        'Distillate Fuel Oil', 'Bio-fuel Oil',
                        'Bio-Petroleum Fuel Oil', 'Natural Plant Oil',
                        'Other'],
    'Residual Fuel': ['Refined Product NOS', 'Fuel Oil NOS',
                      'Residual Fuel Oil', 'Bio-Petroleum Fuel Oil',
                      'Natural Plant Oil', 'Other'],
    'Bio Fuel Oil': ['Refined Product NOS', 'Fuel Oil NOS',
                     'Distillate Fuel Oil', 'Residual Fuel Oil',
                     'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil',
                     'Natural Plant Oil', 'Other'],
    'Jet Fuel': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
                 'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil', 'Other'],
    'Kerosene': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
                 'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil', 'Other'],
    'Aviation Gas': ['Refined Product NOS', 'Fuel Oil NOS',
                     'Distillate Fuel Oil', 'Bio-fuel Oil',
                     'Bio-Petroleum Fuel Oil', 'Other'],
    'MDO': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
            'Residual Fuel Oil', 'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil',
            'Other'],
    'Diesel': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
               'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil', 'Other'],
    'IFO': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
            'Residual Fuel Oil', 'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil',
            'Other'],
    'HFO': ['Refined Product NOS', 'Fuel Oil NOS', 'Distillate Fuel Oil',
            'Residual Fuel Oil', 'Bio-fuel Oil', 'Bio-Petroleum Fuel Oil',
            'Other'],
    'Lube Oil': ['Refined Product NOS', 'Lube Oil', 'Other'],
    'Refinery Intermediate': ['Bitumen Blend', 'Refined Product NOS',
                              'Lube Oil', 'Other'],
    'Natural Plant Oil': ['Bio-fuel Oil', 'Bio-Petroleum Fuel Oil', 'Lube Oil',
                          'Natural Plant Oil', 'Other'],
    'Dielectric Oil': ['Refined Product NOS', 'Dielectric Oil', 'Other'],
    'Transformer Oil': ['Refined Product NOS', 'Dielectric Oil', 'Other'],
    'Tight Oil': ['Crude Oil NOS', 'Other'],
}


labels_to_types = ManyMany(_label_to_types)


@dataclass_to_json
@dataclass
class Label:
    '''
        So Labels will be a collection terms that the user can use to
        narrow down the list of oils he/she is interested in.
    '''
    name: str
