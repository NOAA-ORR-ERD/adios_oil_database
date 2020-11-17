'''
    This is where we handle the initialization of the oil labels.

    Basically, we have a number of oil labels which will make it possible
    for users to find oils by the general 'type' of oil they are looking for.

    So we would like each oil to be linked to one or more of these
    labels.  For most of the oils we should be able to do this using
    generalized methods.  But there will very likely be some records
    we just have to link in a hard-coded way.

    The selection criteria for assigning refined products to different
    labels depends upon the API (density) and the viscosity at a given
    temperature, usually at 38 C(100F).  The criteria follows closely,
    but not identically, to the ASTM standards
'''
import logging

from oil_database.data_sources.oil import OilEstimation
from oil_database.models.common.label import labels_to_types

logger = logging.getLogger(__name__)


def load_labels(db):
    for name, product_types in labels_to_types.left.items():
        db.label.insert_one({'name': name,
                             'product_types': list(product_types)})


def print_all_labels(db):
    logger.info('Labels in the database...')

    for label in db.label.find({}):
        logger.info(f'\t{label["name"]}')


def link_oil_to_labels(oil):
    '''
        Here, we have a single oil and we would like to link it to one or more
        labels based on its properties.
    '''
    try:
        labels = oil['metadata']['labels']
    except TypeError:
        labels = oil.metadata.labels
    except KeyError:
        labels = []

    sample = OilEstimation(oil).get_sample()

    if sample is None:
        logger.warn('oil: {} has no fresh sample.  Skipping Categorization.'
                    .format(oil['oil_id']))
        return

    if is_crude_light(oil):
        labels.extend(['Crude', 'Light'])

    if is_crude_medium(oil):
        labels.extend(['Crude', 'Medium'])

    if is_crude_heavy(oil):
        labels.extend(['Crude', 'Heavy'])

    if is_refined_fuel_oil_1(oil, sample):
        labels.extend(['Refined',
                       'Light',
                       'Fuel Oil 1',
                       'Gasoline',
                       'Kerosene'])

    if is_refined_fuel_oil_2(oil, sample):
        labels.extend(['Refined',
                       'Fuel Oil 2',
                       'Diesel',
                       'Heating Oil'])

    if is_refined_ifo(oil, sample):
        labels.extend(['Refined',
                       'Intermediate',
                       'Fuel Oil'])

    if is_refined_fuel_oil_6(oil, sample):
        labels.extend(['Refined',
                       'Heavy',
                       'Fuel Oil 6',
                       'HFO',
                       'Bunker',
                       'Group V'])

    if is_generic(oil):
        labels.extend(['Other', 'Generic'])

    if len(labels) == 0:
        labels.extend(['Other'])

    try:
        oil['metadata']['labels'] = labels
    except TypeError:
        oil.metadata.labels = labels


def is_crude(oil):
    try:
        return ('product_type' in oil['metadata'] and
                oil['metadata']['product_type'] is not None and
                oil['metadata']['product_type'].lower() == 'crude')
    except KeyError:
        return (hasattr(oil.metadata, 'product_type') and
                oil.metadata.product_type is not None and
                oil.metadata.product_type.lower() == 'crude')


def is_refined(oil):
    try:
        return ('product_type' in oil['metadata'] and
                oil['metadata']['product_type'] is not None and
                oil['metadata']['product_type'].lower() == 'refined')
    except KeyError:
        return (hasattr(oil.metadata, 'product_type') and
                oil.metadata.product_type is not None and
                oil.metadata.product_type.lower() == 'refined')


def api_min(oil, oil_api):
    api = oil['metadata'].get('API', None)

    return api is not None and api > oil_api


def api_max(oil, oil_api):
    api = oil['metadata'].get('API', None)

    return api is not None and api < oil_api


def is_crude_light(oil):
    return is_crude(oil) and api_min(oil, 31.1)


def is_crude_medium(oil):
    return is_crude(oil) and api_max(oil, 31.1) and api_min(oil, 22.3)


def is_crude_heavy(oil):
    return is_crude(oil) and api_max(oil, 22.3)


def is_refined_light_products(oil):
    '''
       Category Name:
       - Light Products
       Parent:
       - Refined
       Sample Oils:
       - Cooper Basin Light Naphtha
       - kerosene
       - JP-4
       - avgas
       Density Criteria:
       - API >= 35
       Kinematic Viscosity Criteria:
       - v > 0.0 cSt @ 38 degrees Celcius
    '''
    raise NotImplementedError


def is_refined_fuel_oil_1(oil, sample):
    '''
       Category Name:
       - Fuel oil #1/gasoline/kerosene
       Sample Oils:
       - gasoline
       - kerosene
       - JP-4
       - avgas
       Density Criteria:
       - API >= 35
       Kinematic Viscosity Criteria:
       - v <= 2.5 cSt @ 38 degrees Celcius
    '''
    return (is_refined(oil) and
            api_min(oil, 35.0) and
            is_within_viscosity_range(sample, kvis_max=2.5))


def is_refined_fuel_oil_2(oil, sample):
    '''
       Category Name:
       - Fuel oil #2/Diesel/Heating Oil
       Sample Oils:
       - Diesel
       - Heating Oil
       - No. 2 Distillate
       Density Criteria:
       - 30 <= API < 39
       Kinematic Viscosity Criteria:
       - 2.5 < v <= 4.0 cSt @ 38 degrees Celcius
    '''
    return (is_refined(oil) and
            api_min(oil, 30.0) and
            api_max(oil, 39.0) and
            is_within_viscosity_range(sample, kvis_min=2.5, kvis_max=4.0))


def is_refined_ifo(oil, sample):
    '''
       Category Name:
       - Intermediate Fuel Oil
       Sample Oils:
       - IFO 180
       - Fuel Oil #4
       - Marine Diesel
       Density Criteria:
       - 15 <= API < 30
       Kinematic Viscosity Criteria:
       - 4.0 < v < 200.0 cSt @ 38 degrees Celcius
    '''
    return (is_refined(oil) and
            api_min(oil, 15.0) and
            api_max(oil, 30.0) and
            is_within_viscosity_range(sample, kvis_min=4.0, kvis_max=200.0))


def is_refined_fuel_oil_6(oil, sample):
    '''
       Category Name:
       - Fuel Oil #6/Bunker/Heavy Fuel Oil/Group V
       Sample Oils:
       - Bunker C
       - Residual Oil
       Density Criteria:
       - API < 15
       Kinematic Viscosity Criteria:
       - 200.0 <= v cSt @ 50 degrees Celcius
    '''
    return (is_refined(oil) and
            api_max(oil, 15.0) and
            is_within_viscosity_range(sample, kvis_min=200.0))


def is_generic(oil):
    '''
        Category Name:
        - Other->Generic
        Criteria:
        - Any oils that have been generically generated.  These are found
          in the OilLibTest data file.  Basically these oils have a name
          that is prefixed with '*GENERIC'.
    '''
    try:
        ret = oil['metadata'].get('name', None)
    except AttributeError:
        ret = oil.metadata.name

    if ret is not None:
        return ret.startswith('*GENERIC')
    else:
        return None


def is_within_viscosity_range(oil_sample, kvis_min=None, kvis_max=None):
    category_temp = 273.15 + 38

    viscosity = oil_sample.kvis_at_temp(category_temp)

    if viscosity is None:
        return False

    if kvis_min is not None and kvis_max is not None:
        return (viscosity > kvis_min) and (viscosity <= kvis_max)
    elif kvis_min is not None:
        return viscosity > kvis_min
    elif kvis_max is not None:
        return viscosity <= kvis_max
    else:
        return True
