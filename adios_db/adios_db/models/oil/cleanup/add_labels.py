"""
Add labels to a record -- for those that we can use some automatic criteria for

For a given product type:
    some labels can be determined from API and/or Viscosity ranges.

The criteria follows the ASTM (and others) standards, where we can find them.


"""
from math import inf

from ..product_type import types_to_labels
from ....computation.physical_properties import KinematicViscosity

# # Here are all the Product Types:
# ('Crude Oil NOS',
#  'Tight Oil',
#  'Condensate',
#  'Bitumen Blend',
#  'Bitumen',
#  'Refined Product NOS',
#  'Fuel Oil NOS',
#  'Distillate Fuel Oil',
#  'Residual Fuel Oil',
#  'Refinery Intermediate',
#  'Solvent',
#  'Bio-fuel Oil',
#  'Bio-Petro Fuel Oil',
#  'Natural Plant Oil',
#  'Lube Oil',
#  'Dielectric Oil',
#  'Other')

# # These are the current labels that aren't mapped yet:
# 'Vacuum Gas Oil'

# these are the labels with no criteria for density or viscosity
# e.g, if it's a "Crude Oil NOS", it's a 'Crude Oil'

synonyms_for_product_types = {'Crude Oil',
                              'Shale Oil',
                              'Fracking Oil',
                              'Fuel Oil',
                              'Residual Fuel',
                              'Distillate Fuel',
                              'Refined Product',
                              'Condensate',
                              'Transformer Oil',
                              'Bio-Fuel',
                              }

# If it's an exact match, then it's definitely a synonym
for pt, labels in types_to_labels.labels.items():
    for label in labels:
        if label == pt:
            synonyms_for_product_types.add(label)

# these are labels that are synonymous to other labels
synonyms_for_labels = {
    'Heavy Fuel Oil': ['HFO', 'No. 6 Fuel Oil', 'Bunker C'],
    'Kerosene': ['Jet Fuel'],
    'No. 2 Fuel Oil': ['Diesel', 'Home Heating Oil', 'Gas Oil'],
}

# this maps the labels according to API and kinematic viscosity
# (cSt at given temp in C) ranges.
no_criteria = {"api_min": -inf, "api_max": inf,
               "kvis_min": -inf, "kvis_max": inf,
               "kvis_temp": 15}
label_map = {label: no_criteria for label in synonyms_for_product_types}

label_map.update({
    # 'example_label': {"api_min": -inf, "api_max": inf,
    #                   "kvis_min": -inf, "kvis_max": inf,
    #                   "kvis_temp": None},
    'Condensate': {
        "api_min": 50,
        "api_max": inf,
        "kvis_min": -inf,
        "kvis_max": inf,
        "kvis_temp": 15
    },
    'Light Crude': {
        "api_min": 35,
        "api_max": 50,
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 15
    },
    'Medium Crude': {
        "api_min": 20,
        "api_max": 35,
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 15
    },
    'Heavy Crude': {
        "api_min": -inf,
        "api_max": 20,
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 15
    },
    'Group V': {
        "api_min": -inf,
        "api_max": 10.0,
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 15
    },
    'Heavy Fuel Oil': {
        "api_min": -inf,
        "api_max": 13.4,  # changed to eliminate overlap with IFOs
        #"kvis_min": 381,  # changed from 200 to eliminate overlap with new IFO label criteria
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 50
    },

    # # Bitumen is now a product type, so no need for the critera at all.
    # # pretty much made this up ... non-newtonian
    # #'Bitumen': {"api_min": -inf, "api_max": 10,
    # #            "kvis_min": 1000, "kvis_max": inf, 'kvis_temp': 40},
    # # I went through all the bitumen records that we have, and most of them
    # # do not have kinematic viscosity measurements. However, they all have
    # # dynamic viscosity
    # 'Bitumen': {
    #     "api_min": -inf,
    #     "api_max": 10,
    #     "kvis_min": 1000,
    #     "kvis_max": inf,
    #     'kvis_temp': 40
    # },
    # # I went through all the bitumen records that we have, and most of them
    # # do not have kinematic viscosity measurements. However, they all have
    # # dynamic viscosity measurements which were > 10^6 cP at 0C and > 10^5 cP
    # # at 15C.
    # # I propose changing the criteria to reflect these measurements.

    # Refined light products
    'No. 2 Fuel Oil': {
        "api_min": 30,
        "api_max": 39,
        "kvis_min": 2,  # changed from 2.5 because it didn't accommodate all the existing records
        "kvis_max": 4,
        'kvis_temp': 38
    },
    'Kerosene': {
        "api_min": 43,  # changed from 47.6 because it didn't accommodate all the existing records
        "api_max": 54.4,  # changed from 67.8 to avoid overlap with gasoline
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 38
    },
    'Aviation Gas': {
        "api_min": 47.6,
        "api_max": 73,  # changed from 70.8 because it didn't accommodate all the existing records
        "kvis_min": -inf,
        "kvis_max": inf,
        'kvis_temp': 38
    },
    'Gasoline': {
        "api_min": 54.5,  # changed from 59.9 because it didn't accommodate all the existing records
        "api_max": 76.6,
        "kvis_min": -inf,
        "kvis_max": 2.5,
        'kvis_temp': 38
    },
    # Intermediate Fuel Oils
    'MDO': {
        "api_min": 27,  # changed from 30 to accommodate ISO 8217 specs
        "api_max": 42,
        "kvis_min": -inf,
        "kvis_max": 11,
        'kvis_temp': 40
    },
    'IFO': {
        "api_min": 13.4,  # changed from 15 to accommodate existing IFO180 records
        "api_max": 30,
        "kvis_min": 4,
        "kvis_max": 380,  # changed from 200 at 38C to capture oils that are more viscous than IFO180
        'kvis_temp': 50
    },
})

for label, synonyms in synonyms_for_labels.items():
    label_map.update({syn: label_map[label] for syn in synonyms})


def get_sulfur_labels(oil):
    """
    the low sulfur labels are their own thing
    """
    # Sulfur limits in percent
    L_limit = 1.5  # fixme -- this may not be right!
    V_limit = 0.5
    U_limit = 0.1
    labels = set()
    if oil.sub_samples:  # probably only comes up in tests, but ...
        for compound in oil.sub_samples[0].bulk_composition:
            if 'sulfur' in compound.name.lower():
                sulfur = compound.measurement.converted_to('%').maximum
                if sulfur <= U_limit:
                    labels.add('ULSFO')
                if sulfur <= V_limit:
                    labels.add('VLSFO')
                if sulfur <= L_limit:
                    labels.add('LSFO')

    return labels


def get_suggested_labels(oil):
    """
    get the labels suggested for this oil

    :param oil: the oil object to get the labels for
    :type oil: Oil object

    :returns: sorted list of all labels that match the criteria
    """
    labels = set()
    pt = oil.metadata.product_type

    # everything gets its product type as a label as well
    # unless it has no product type
    if pt == "Other":  # we don't want any labels auto added for Other
        return []
    try:
        for label in types_to_labels.left[oil.metadata.product_type]:
            if is_label(oil, label):
                labels.add(label)
    except KeyError:
        pass

    # Add the sulfur labels
    labels |= get_sulfur_labels(oil)

    # sorting so they'll be in consistent order
    return sorted(labels)


def add_labels_to_oil(oil):
    """
    add labels to the passed in oil.

    this adds labels, but does not remove any existing ones

    :param oil: the oil object to add labels to
    :type oil: Oil object
    """
    labels = set(oil.metadata.labels)

    for label in types_to_labels.left['oil.metadata.product_type']:
        if is_label(oil, label):
            labels.add(label)

    oil.metadata.labels = sorted(labels)


def is_label(oil, label):
    try:
        data = label_map[label]
    except KeyError:
        return False

    api = oil.metadata.API
    #if label == 'Heavy Fuel Oil':
        #print(f'{data=}')
        #print(f'{api=}')
    # check API:
    if ((data['api_min'] != -inf) or (data['api_max'] != inf)):
        if (api is not None and data['api_min'] <= api < data['api_max']):
            is_label = True
        else:
            is_label = False
    else:
        is_label = True

    if is_label and ((data['kvis_min'] != -inf) or
                     (data['kvis_max'] != inf)):  # check viscosity limits
        try:
            KV = KinematicViscosity(oil)
            kvis = KV.at_temp(temp=data['kvis_temp'], kvis_units='cSt',
                              temp_units='C')
            print(f"{kvis=}")
            is_label = True if data['kvis_min'] <= kvis < data['kvis_max'] else False
        except (ZeroDivisionError, ValueError):
            # if it can't do this, we don't apply the label
            is_label = True

    return is_label
