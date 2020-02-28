"""
Validation of a single oil record


Currently, this is essentially a placeholder, so we have something to use in the client.
It does about as little as it can, while still working

The top-level interface is a single function:

validate(pyjson_of_an_oil_record)

(pyjson is a python dict that is a match for the JSON)

It will add the validation messages to the "status" field of the record.


Currently, it converts the pyjson into a .oil/Oil object, then validates on that.


NOTE: this needs a LOT more, and a massive refactor.

A few ideas about that:

* There should be some automated way to discover all the validators, so we can
   simply add more in one place, and be done.

* Maybe validator classes? that way we can subclass to make a lot of similar
  ones without duplicating code.
"""

from ..oil import Oil

import logging

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)

# Putting these all here so we can keep track more easily
from .warnings import WARNINGS
from .errors import ERRORS


def api_kludge(oil_json):
    """
    This it get the API from the zeroth sub_record, where it should not be anyway :-(

    See: https://gitlab.orr.noaa.gov/erd/oil_database/issues/77
    """
    try:
        oil_json['api'] = oil_json['samples'][0]['apis'][0]['gravity']
    except (KeyError, IndexError):
        # if there are no samples,
        #  or no apis in the zeroth sample
        oil_json['api'] = None


def validate(oil_json):
    """
    validate the oil record.

    validation messages are added to the status field of the record

    :param oil: The oil record to be validated, in json-compatible python data structure.

    """

    # make an oil object out of it:
    if 'api' not in oil_json:
        api_kludge(oil_json)
    try:
        oil = Oil.from_py_json(oil_json)
    except TypeError as err:
        if "argument: 'name'" in err.args[0]:
            oil_json["status"] = ERRORS["E001"]
            return
        else:  # some other TypeError
            raise

    messages = set()
    for val_fun in VALIDATORS:
        msg = val_fun(oil)
        if msg:
            messages.add(msg)

    oil_json["status"] = list(messages)


def val_has_reasonable_name(oil):
    """
    right now, reasonable is more than 5 characters

    we may want to add more later
    """
    if len(oil.name.strip()) < 5:
        return WARNINGS["W001"].format(oil=oil)
    else:
        return None


def val_has_product_type(oil):
    '''
    Oil records should have a product type
    '''
    valid_types = ('crude',
                   'refined',
                   'bitumen product',
                   'other')

    if not oil.product_type:
        return WARNINGS["W002"]
    elif not oil.product_type.lower() in ('crude',
                                          'refined',
                                          'bitumen product',
                                          'other'):
        return WARNINGS["W003"].format(oil.product_type, valid_types)
    else:
        return None


def val_check_api(oil):
    api = oil.api
    ptype = oil.product_type
    if ptype and ptype.lower() == "crude":
        if api is None:
            return ERRORS["E002"]
    else:
        if api is None:
            return WARNINGS["W004"]
    if not (-60.0 < api < 100):  # somewhat arbitrary limits
        return WARNINGS["W005"].format(api=api)


def val_check_for_samples(oil):
    if not oil.samples:
        return ERRORS["E003"]


def val_check_for_densities(oil):
    # note: would be good to be smart about temp densities are at
    if not oil.samples:
        return WARNINGS["W006"]

    if not oil.samples[0].densities:
        return WARNINGS["W006"]

    return None


def val_check_for_distillation_cuts(oil):
    try:
        sample = oil.samples[0]
    except (AttributeError, IndexError):
        return None
    print(sample.cuts)
    try:
        if not sample.cuts:
            return WARNINGS["W007"]
    except AttributeError:
        return WARNINGS["W007"]
    return None


# build a list of all the validators:

VALIDATORS = [ val for name, val in vars().items() if name.startswith("val_")]




def oil_record_validation(oil):
    '''
    Validate an oil record and return a list of error messages
    '''
    errors = []

    if not has_product_type(oil):
        errors.append('W002: Imported record has no product type')

    if not has_api_or_densities(oil):
        errors.append('E001: Imported record has no density information')

    if not has_viscosities(oil):
        errors.append('E001: Imported record has no viscosity information')

    if not has_distillation_cuts(oil):
        errors.append('W002: Imported record has insufficient '
                      'distillation cut data')

    return errors


# def has_product_type(oil):
#     '''
#     In order to perform estimations, we need to determine if we are
#     dealing with a crude or refined oil product.  We cannot continue
#     if this information is missing.
#     '''
#     if (oil.product_type is None or
#         oil.product_type.lower() in ('crude', 'refined',
#                                      'bitumen product' 'other')):
#         return True

#     return False


# def has_api_or_densities(oil):
#     '''
#     In order to perform estimations, we need to have at least one
#     density measurement.  We cannot continue if this information
#     is missing.

#     This is just a primitive test, so we do not evaluate the quantities,
#     simply that some kind of value exists.
#     '''
#     if has_api(oil):
#         return True
#     elif len(list(oil.densities)) > 0:
#         return True
#     else:
#         return False


# def has_api(oil):
#     '''
#         Env Canada record has multiple weathered APIs, so we need to account
#         for that.
#     '''
#     if oil.apis is not None and len(list(oil.apis)) > 0:
#         return True
#     else:
#         return False


# def has_viscosities(oil):
#     '''
#         In order to perform estimations, we need to have at least one
#         viscosity measurement.  We cannot continue if this information
#         is missing.
#         This is just a primitive test, so we do not evaluate the quantities,
#         simply that some kind of value exists.
#     '''
#     if (hasattr(oil, 'kvis') and
#             oil.kvis is not None and
#             len(list(oil.kvis)) > 0):
#         return True
#     elif (hasattr(oil, 'dvis') and
#             oil.dvis is not None and
#             len(list(oil.dvis)) > 0):
#         return True
#     else:
#         return False


# def has_distillation_cuts(oil):
#     '''
#         - In order to perform estimations on a refined product, we need to have
#           at least three distillation cut measurements.  We cannot continue
#           if this information is missing.
#         - For crude oil products, we can estimate cut information from its
#           API value if the cuts don't exist.
#         - If we have no cuts and no API, we can still estimate cuts by
#           converting density to API, and then API to cuts.
#         - This is just a primitive test, so we do not evaluate the quantities,
#           simply that some kind of value exists.
#     '''
#     if (oil.product_type is not None and
#             oil.product_type.lower() == 'crude'):
#         if (len(list(oil.cuts)) >= 3 or
#                 has_api_or_densities(oil)):
#             return True  # cuts can be estimated if not present
#         else:
#             return False
#     else:
#         if len(list(oil.cuts)) >= 3:
#             return True
#         else:
#             return False


# def has_densities_below_pour_point(oil):
#     '''
#         This may be presumptuous, but I believe the volumetric coefficient
#         that we use for calculating densities at temperature are probably for
#         oils in the liquid phase.  So we would like to check if any
#         densities in our oil fall below the pour point.

#         Note: Right now we won't worry about estimating the pour point
#               if the pour point data points don't exist for the record,
#               then we will assume that our densities are probably fine.
#     '''
#     try:
#         pp_max = oil.pour_point_max_k
#         pp_min = oil.pour_point_min_k
#         pour_point = min([pp for pp in (pp_min, pp_max) if pp is not None])
#     except (ValueError, TypeError):
#         pour_point = None

#     if pour_point is None:
#         return False
#     else:
#         rho_temps = [d.ref_temp_k for d in oil.densities
#                      if d.ref_temp_k is not None]
#         if oil.api is not None:
#             rho_temps.append(288.15)

#         if any([(t < pour_point) for t in rho_temps]):
#             try:
#                 oil_id = oil.adios_oil_id
#             except AttributeError:
#                 oil_id = oil.oil_id

#             print('\toil_id: {}, pour_point: {}, rho_temps: {}, lt: {}'
#                   .format(oil_id, pour_point, rho_temps,
#                           [(t < pour_point) for t in rho_temps]))
#             return True


# def oil_api_matches_density(oil):
#     '''
#         The oil API should pretty closely match its density at 15C.

#         Note: we will need to rework this function.  Return True for now.
#     '''
#     return True
