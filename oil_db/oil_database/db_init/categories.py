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

from slugify import slugify_filename

from pymodm.errors import MultipleObjectsReturned, DoesNotExist

import unit_conversion as uc

from oil_database.models.common import Category
from oil_database.data_sources.noaa_fm import OilLibraryCsvFile
from oil_database.data_sources.oil import OilEstimation

from oil_database.models.oil import Oil

logger = logging.getLogger(__name__)


def process_categories(settings):
    logger.info('Loading Categories...')
    load_categories()
    logger.info('Finished!!!')

    print_all_categories()

    link_oils_to_categories(settings)


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

    crude.append(Category(name='Condensate'))
    crude.append(Category(name='Light'))
    crude.append(Category(name='Medium'))
    crude.append(Category(name='Heavy'))

    refined.append(Category(name='Light Products (Fuel Oil 1)'))
    refined.append(Category(name='Gasoline'))
    refined.append(Category(name='Kerosene'))

    refined.append(Category(name='Fuel Oil 2'))
    refined.append(Category(name='Diesel'))
    refined.append(Category(name='Heating Oil'))

    refined.append(Category(name='Intermediate Fuel Oil'))

    refined.append(Category(name='Fuel Oil 6 (HFO)'))
    refined.append(Category(name='Bunker'))
    refined.append(Category(name='Heavy Fuel Oil'))
    refined.append(Category(name='Group V'))

    other.append(Category(name='Other'))
    other.append(Category(name='Generic'))

    crude.save()
    refined.save()
    other.save()


def print_all_categories():
    logger.info('Here are our newly built categories...')

    for parent in Category.objects.raw({'parent': None}):
        for child in list_categories(parent):
            logger.info(child)


def list_categories(category, indent=0):
    '''
        This is a recursive method to print out our categories
        showing the nesting with tabbed indentation.
    '''
    yield '{0}{1}'.format(' ' * indent, category.name)

    for c in category.children:
        for y in list_categories(c, indent + 4):
            yield y


def link_oils_to_categories(settings):
    # now we try to link the oil records with our categories
    # in some kind of automated fashion
    link_crude_light_oils()
    link_crude_medium_oils()
    link_crude_heavy_oils()

    link_refined_fuel_oil_1()
    link_refined_fuel_oil_2()
    link_refined_ifo()
    link_refined_fuel_oil_6()

    link_generic_oils()
    link_all_other_oils()

    manually_recategorize_oils(settings)

    show_uncategorized_oils()


def link_crude_light_oils():
    # our category
    top, categories = get_categories_by_names('Crude', ('Light',))

    oils = get_oils_by_api('crude', api_min=31.1)

    count = 0
    for o in oils:
        o.categories.extend(categories)
        o.save()
        count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_crude_medium_oils():
    # our category
    top, categories = get_categories_by_names('Crude', ('Medium',))

    oils = get_oils_by_api('crude', api_min=22.3, api_max=31.1)

    count = 0
    for o in oils:
        o.categories.extend(categories)
        o.save()
        count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_crude_heavy_oils():
    top, categories = get_categories_by_names('Crude', ('Heavy',))

    oils = get_oils_by_api('crude', api_max=22.3)

    count = 0
    for o in oils:
        o.categories.extend(categories)
        o.save()
        count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_refined_light_products():
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


def link_refined_fuel_oil_1():
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
    top, categories = get_categories_by_names('Refined',
                                              ('Light Products (Fuel Oil 1)',
                                               'Gasoline',
                                               'Kerosene'))

    oils = get_oils_by_api('refined', api_min=35.0)

    count = 0
    for o in oils:
        if oil_within_viscosity_range(o, kvis_max=2.5):
            o.categories.extend(categories)
            o.save()
            count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_refined_fuel_oil_2():
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
    top, categories = get_categories_by_names('Refined',
                                              ('Fuel Oil 2',
                                               'Diesel',
                                               'Heating Oil'))

    oils = get_oils_by_api('refined', api_min=30.0, api_max=39.0)

    count = 0
    for o in oils:
        if oil_within_viscosity_range(o, kvis_min=2.5, kvis_max=4.0):
            o.categories.extend(categories)
            o.save()
            count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_refined_ifo():
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
    top, categories = get_categories_by_names('Refined',
                                              ('Intermediate Fuel Oil',))

    oils = get_oils_by_api('refined', api_min=15.0, api_max=30.0)

    count = 0
    for o in oils:
        if oil_within_viscosity_range(o, kvis_min=4.0, kvis_max=200.0):
            o.categories.extend(categories)
            o.save()
            count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_refined_fuel_oil_6():
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
    top, categories = get_categories_by_names('Refined',
                                              ('Fuel Oil 6',
                                               'Bunker',
                                               'Heavy Fuel Oil',
                                               'Group V'))

    oils = get_oils_by_api('refined', api_min=0.0, api_max=15.0)

    count = 0
    for o in oils:
        if oil_within_viscosity_range(o, kvis_min=200.0):
            o.categories.extend(categories)
            o.save()
            count += 1

    logger.info('{0} oils added to {1} -> {2}.'
                .format(count, top.name, [n.name for n in categories]))


def link_generic_oils():
    '''
        Category Name:
        - Other->Generic
        Criteria:
        - Any oils that have been generically generated.  These are found
          in the OilLibTest data file.  Basically these oils have a name
          that is prefixed with '*GENERIC'.
    '''
    _top, categories = get_categories_by_names('Other', ('Generic',))

    oils = (Oil.objects.raw({'name': {'$regex': r'\*GENERIC*'}}).all())

    count = 0
    for o in oils:
        o.categories.extend(categories)
        o.save()
        count += 1

    logger.info('{0} oils added to {1}.'
                .format(count, [n.name for n in categories]))


def link_all_other_oils():
    '''
        Category Name:
        - Other
        Sample Oils:
        - Catalytic Cracked Slurry Oil
        - Fluid Catalytic Cracker Medium Cycle Oil
        Criteria:
        - Any oils that fell outside all the other Category Criteria
    '''
    _top, categories = get_categories_by_names('Other',
                                               ('Other',))

    oils = (Oil.objects.raw({'categories.0': {'$exists': False}}).all())

    count = 0
    for o in oils:
        o.categories.extend(categories)
        o.save()
        count += 1

    logger.info('{0} oils added to {1}.'
                .format(count, [n.name for n in categories]))


def manually_recategorize_oils(settings):
    '''
        When we categorize oils, there is a lot of overlap in their criteria
        that results in oils added to categories when it is fairly clear
        they should not be a part of that category.

        A smaller, but similar, problem is an oil that should be included
        in a category, but its criteria falls outside that of said category
        and it is not added.

        Here we provide a whitelist/blacklist mechanism for manually adding
        and removing oils from categories after the automatic categorization
        processes have completed.
    '''
    fn = settings['blacklist.file']
    fd = OilLibraryCsvFile(fn)
    logger.info('blacklist file version: {}'.format(fd.__version__))

    logger.info('Re-categorizing oils in our blacklist')
    rowcount = 0
    for r in fd.readlines():
        r = [unicode(f, 'utf-8') if f is not None else f
             for f in r]
        recategorize_oil(fd.file_columns, r)
        rowcount += 1

    logger.info('Re-categorization finished!!!  {0} rows processed.'
                .format(rowcount))


def recategorize_oil(file_columns, row_data):
    file_columns = [slugify_filename(c).lower()
                    for c in file_columns]
    row_dict = dict(zip(file_columns, row_data))

    try:
        oil_obj = Oil.objects.get({'adios_oil_id': row_dict['adios_oil_id']})
    except Exception:
        logger.error('Re-categorize: could not query oil {}({})'
                     .format(row_dict['oil_name'],
                             row_dict['adios_oil_id']))
        return

    logger.info('Re-categorizing oil: {},\n'
                '\t from: {},\n'
                '\t to: {}'
                .format(oil_obj.name,
                        row_dict['remove_from'],
                        row_dict['add_to']))

    remove_from_categories(oil_obj, row_dict['remove_from'])
    add_to_categories(oil_obj, row_dict['add_to'])


def update_oil_in_categories(oil_obj, categories, func):
    for c in categories.split(','):
        c = c.strip()
        cat_obj = get_category_by_name(c)

        if cat_obj is not None:
            func(oil_obj, cat_obj)
        else:
            logger.error('\t{}("{}", "{}"): Category not accessible'
                         .format(func.__name__, oil_obj.name, c))


def get_category_by_name(name):
    '''
        Get the category matching a name.
        - Category name can be a simple name, or a full path to a category
          inside the Category hierarchy.
        - A full path consists of a sequence of category names separated by
          '->' e.g. 'Refined->Gasoline'
    '''
    full_path = name.split('->')
    if len(full_path) > 1:
        # Traverse the path and verify all categories are linked.
        # The last one we find in our traversal is the one we want.
        try:
            parent = None

            for cat_name in full_path:
                cat_obj = (Category.objects.get({'name': cat_name,
                                                 'parent': parent}))

                parent = cat_obj._id
        except Exception:
            cat_obj = None
    else:
        # just a simple name
        try:
            cat_obj = Category.objects.get({'name': name})
        except Exception:
            cat_obj = None

    return cat_obj


def remove_from_categories(oil_obj, categories):
    update_oil_in_categories(oil_obj, categories, remove_from_category)


def remove_from_category(oil_obj, category):
    if category in oil_obj.categories:
        logger.debug('\tRemove category {} from oil {}'
                     .format(category.name, oil_obj.name))
        oil_obj.categories.remove(category)
        oil_obj.save()

    assert category not in oil_obj.categories


def add_to_categories(oil_obj, categories):
    update_oil_in_categories(oil_obj, categories, add_to_category)


def add_to_category(oil_obj, category):
    if category not in oil_obj.categories:
        logger.debug('\tAdd category {} to oil {}'
                     .format(category.name, oil_obj.name))
        oil_obj.categories.append(category)
        oil_obj.save()

    assert category in oil_obj.categories


def show_uncategorized_oils():
    oils = (Oil.objects.raw({'categories.0': {'$exists': False}}).all())

    fd = open('temp.txt', 'w')
    fd.write('adios_oil_id\t'
             'product_type\t'
             'api\t'
             'viscosity\t'
             'pour_point\t'
             'name\n')

    logger.info('{0} oils uncategorized.'.format(oils.count()))

    for o in oils:
        o_estim = OilEstimation(o)
        if o.api >= 0:
            if o.api < 15:
                category_temp = 273.15 + 50
            else:
                category_temp = 273.15 + 38

            viscosity = uc.convert('Kinematic Viscosity', 'm^2/s', 'cSt',
                                   o_estim.kvis_at_temp(category_temp))
        else:
            viscosity = None

        fd.write('{0.imported.adios_oil_id}\t'
                 '{0.imported.product_type}\t'
                 '{0.api}\t'
                 '{1}\t'
                 '({0.pour_point_min_k}, {0.pour_point_max_k})\t'
                 '{0.name}\n'
                 .format(o, viscosity))


def get_oils_by_api(product_type, api_min=None, api_max=None):
    '''
        After we have performed our Oil estimations, all oils should have a
        valid API value.
    '''
    query_args = {'product_type': product_type.lower(),
                  'apis.weathering': 0.0}

    if api_min is not None or api_max is not None:
        query_args.update({'apis.gravity': {}})

        if api_min is not None:
            query_args['apis.gravity'].update({'$gt': api_min})

        if api_max is not None:
            query_args['apis.gravity'].update({'$lte': api_max})

    return Oil.objects.raw(query_args).all()


def get_categories_by_names(top_name, child_names):
    '''
        Get the top level category by name, and a list of child categories
        directly underneath it by their names.

        This is a utility function that serves some common functionality in
        our various categorization functions.  Probably not useful outside
        of this module.
    '''
    try:
        top_category = Category.objects.get({'parent': None,
                                             'name': top_name})
    except MultipleObjectsReturned as ex:
        ex.message = ('Multiple top categories named "{}" found.'
                      .format(top_name))
        ex.args = (ex.message, )

        raise ex
    except DoesNotExist:
        ex.message = ('Top category "{}" not found.'.format(top_name))
        ex.args = (ex.message, )

        raise ex

    child_categories = [c for c in top_category.children
                        if c.name in child_names]

    return top_category, child_categories


def oil_within_viscosity_range(oil_obj, kvis_min=None, kvis_max=None):
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
