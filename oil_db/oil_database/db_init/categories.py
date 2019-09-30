'''
    This is where we handle the initialization of the oil categories.

    Basically, we have a number of oil categories arranged in a tree
    structure.  This will make it possible to create an expandable and
    collapsible way for users to find oils by the general 'type' of oil
    they are looking for, starting from very general types and navigating
    to more specific types.

    So we would like each oil to be linked to one or more of these
    categories.  For most of the oils we should be able to do this using
    generalized methods.  But there will very likely be some records
    we just have to link in a hard-coded way.

    The selection criteria for assigning refined products to different
    categories on the oil selection screen, depends upon the API (density)
    and the viscosity at a given temperature, usually at 38 C(100F).
    The criteria follows closely, but not identically, to the ASTM standards
'''
import logging

from functools import lru_cache

import unit_conversion as uc

from oil_database.models.common import Category
from oil_database.data_sources.oil import OilEstimation

logger = logging.getLogger(__name__)


def load_categories():
    '''
        Note: When saving a PyMODM object, any attributes that contain
              document references will be checked for the saved state of the
              referenced object.
              And because we are working with doubly linked parent/child
              relationships here, it is important to save the object early
              before any links are established.
    '''
    crude = Category(name='Crude').save()
    refined = Category(name='Refined').save()
    other = Category(name='Other').save()

    crude.append(Category(name='Condensate').save())
    crude.append(Category(name='Light').save())
    crude.append(Category(name='Medium').save())
    crude.append(Category(name='Heavy').save())

    refined.append(Category(name='Light Products (Fuel Oil 1)').save())
    refined.append(Category(name='Gasoline').save())
    refined.append(Category(name='Kerosene').save())

    refined.append(Category(name='Fuel Oil 2').save())
    refined.append(Category(name='Diesel').save())
    refined.append(Category(name='Heating Oil').save())

    refined.append(Category(name='Intermediate Fuel Oil').save())

    refined.append(Category(name='Fuel Oil 6 (HFO)').save())
    refined.append(Category(name='Bunker').save())
    refined.append(Category(name='Heavy Fuel Oil').save())
    refined.append(Category(name='Group V').save())

    other.append(Category(name='Other').save())
    other.append(Category(name='Generic').save())


def list_categories(category, indent=0):
    '''
        This is a recursive method to print out our categories
        showing the nesting with tabbed indentation.
    '''
    yield ('{}{}'.format(' ' * indent, category.name))

    for c in category.expand('children'):
        for y in list_categories(c, indent + 4):
            yield y


def print_all_categories():
    logger.info('Here are our newly built categories...')

    for parent in Category.find(filter={'parent': None}):
        for child in list_categories(parent):
            logger.info(child)


@lru_cache(maxsize=128)
def get_categories_by_names(top_name, child_names):
    '''
        Get the top level category by name, and a list of child categories
        directly underneath it by their names.
    '''
    top_category = Category.find_one({'parent': None, 'name': top_name})

    if top_category is None:
        return None

    child_categories = [c for c in top_category.children
                        if c.name in child_names]

    return child_categories


def link_oil_to_categories(oil):
    '''
        Here, we have a single oil and we would like to link it to one or more
        categories based on its properties.
        This is similar to the batch processing function above.
    '''
    oil.categories = []

    if is_crude_light(oil):
        # add crude->light
        categories = get_categories_by_names('Crude', ('Light',))
        oil.categories.extend(categories)

    if is_crude_medium(oil):
        categories = get_categories_by_names('Crude', ('Medium',))
        oil.categories.extend(categories)

    if is_crude_heavy(oil):
        categories = get_categories_by_names('Crude', ('Heavy',))
        oil.categories.extend(categories)

    if is_refined_fuel_oil_1(oil):
        categories = get_categories_by_names('Refined',
                                             ('Light Products (Fuel Oil 1)',
                                              'Gasoline',
                                              'Kerosene'))
        oil.categories.extend(categories)

    if is_refined_fuel_oil_2(oil):
        categories = get_categories_by_names('Refined',
                                             ('Fuel Oil 2',
                                              'Diesel',
                                              'Heating Oil'))
        oil.categories.extend(categories)

    if is_refined_ifo(oil):
        categories = get_categories_by_names('Refined',
                                             ('Intermediate Fuel Oil',))
        oil.categories.extend(categories)

    if is_refined_fuel_oil_6(oil):
        categories = get_categories_by_names('Refined',
                                             ('Fuel Oil 6 (HFO)',
                                              'Bunker',
                                              'Heavy Fuel Oil',
                                              'Group V'))
        oil.categories.extend(categories)

    if is_generic(oil):
        categories = get_categories_by_names('Other', ('Generic',))
        oil.categories.extend(categories)

    if len(oil.categories) == 0:
        categories = get_categories_by_names('Other', ('Other',))
        oil.categories.extend(categories)


def is_crude(oil):
    return (oil.product_type is not None and
            oil.product_type.lower() == 'crude')


def is_refined(oil):
    return (oil.product_type is not None and
            oil.product_type.lower() == 'refined')


def api_min(oil, oil_api):
    apis = [a for a in oil.apis if a.weathering == 0.0]

    return (len(apis) > 0 and apis[0].gravity > oil_api)


def api_max(oil, oil_api):
    apis = [a for a in oil.apis if a.weathering == 0.0]

    return (len(apis) > 0 and apis[0].gravity < oil_api)


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


def is_refined_fuel_oil_1(oil):
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
            is_within_viscosity_range(oil, kvis_max=2.5))


def is_refined_fuel_oil_2(oil):
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
            is_within_viscosity_range(oil, kvis_min=2.5, kvis_max=4.0))


def is_refined_ifo(oil):
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
            is_within_viscosity_range(oil, kvis_min=4.0, kvis_max=200.0))


def is_refined_fuel_oil_6(oil):
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
            is_within_viscosity_range(oil, kvis_min=200.0))


def is_generic(oil):
    '''
        Category Name:
        - Other->Generic
        Criteria:
        - Any oils that have been generically generated.  These are found
          in the OilLibTest data file.  Basically these oils have a name
          that is prefixed with '*GENERIC'.
    '''
    return oil.name.startswith('*GENERIC')


def is_within_viscosity_range(oil_obj, kvis_min=None, kvis_max=None):
    category_temp = 273.15 + 38

    o_estim = OilEstimation(oil_obj)

    if o_estim.kvis_at_temp(category_temp) is None:
        return False

    # TODO: It seems clunky to have to convert using the unit_conversion
    #       package directly.  It seems that maybe we want kvis_at_temp()
    #       to return a KinematicViscosityUnit type.
    #       We should maybe define the API of the estimation object more
    #       consistently.
    viscosity = uc.convert('Kinematic Viscosity', 'm^2/s', 'cSt',
                           o_estim.kvis_at_temp(category_temp))

    if kvis_min is not None and kvis_max is not None:
        return (viscosity > kvis_min) and (viscosity <= kvis_max)
    elif kvis_min is not None:
        return viscosity > kvis_min
    elif kvis_max is not None:
        return viscosity <= kvis_max
    else:
        return True
