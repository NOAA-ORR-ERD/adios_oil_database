"""
Validation of a single oil record

NOTE: this needs a LOT more, and a massive refactor.

A few ideas about that:

This needs to work with the JSON, not classes!

* Individual validation functions should contain their error messages, etc.

* There should be some automated way to discover all the validators, so we can
   simply add more in one place, and be done.

* Maybe validator classes? that way we can subclass to make a lot of similar
  ones without duplicating code.
"""

import logging

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


class OilRejected(Exception):
    '''
        Custom exception for Oil initialization that we can raise if we
        decide we need to reject an oil record for any reason.
    '''

    def __init__(self, message, oil_name, *args):
        # without this you may get DeprecationWarning
        self.message = message

        # Special attribute you desire with your Error,
        # perhaps the value that caused the error?:
        self.oil_name = oil_name

        # allow users initialize misc. arguments as any other builtin Error
        super().__init__(message, oil_name, *args)

    def __repr__(self):
        return '{0}(oil={1}, errors={2})'.format(self.__class__.__name__,
                                                 self.oil_name,
                                                 self.message)

# ### Oil Quality checks
#
# FIXME: At the very least, the checks should return the error message,
#        rather than having a separate mapping. But this needs major
#        refactoring anyway


def oil_record_validation(oil):
    '''
    Validate an oil record and return a list of error messages
    '''
    errors = []

    if not has_product_type(oil):
        errors.append('W001: Imported record has no product type')

    if not has_api_or_densities(oil):
        errors.append('E001: Imported record has no density information')

    if not has_viscosities(oil):
        errors.append('E001: Imported record has no viscosity information')

    if not has_distillation_cuts(oil):
        errors.append('W001: Imported record has insufficient distillation cut data')

    return errors


def has_product_type(oil):
    '''
    In order to perform estimations, we need to determine if we are
    dealing with a crude or refined oil product.  We cannot continue
    if this information is missing.
    '''
    if (oil.product_type is None or
        oil.product_type.lower() in ('crude', 'refined',
                                     'bitumen product' 'other')):
        return True

    return False


def has_api_or_densities(oil):
    '''
    In order to perform estimations, we need to have at least one
    density measurement.  We cannot continue if this information
    is missing.

    This is just a primitive test, so we do not evaluate the quantities,
    simply that some kind of value exists.
    '''
    if has_api(oil):
        return True
    elif len(list(oil.densities)) > 0:
        return True
    else:
        return False


def has_api(oil):
    '''
        Env Canada record has multiple weathered APIs, so we need to account
        for that.
    '''
    if oil.apis is not None and len(list(oil.apis)) > 0:
        return True
    else:
        return False


def has_viscosities(oil):
    '''
        In order to perform estimations, we need to have at least one
        viscosity measurement.  We cannot continue if this information
        is missing.
        This is just a primitive test, so we do not evaluate the quantities,
        simply that some kind of value exists.
    '''
    if (hasattr(oil, 'kvis') and
            oil.kvis is not None and
            len(list(oil.kvis)) > 0):
        return True
    elif (hasattr(oil, 'dvis') and
            oil.dvis is not None and
            len(list(oil.dvis)) > 0):
        return True
    else:
        return False


def has_distillation_cuts(oil):
    '''
        - In order to perform estimations on a refined product, we need to have
          at least three distillation cut measurements.  We cannot continue
          if this information is missing.
        - For crude oil products, we can estimate cut information from its
          API value if the cuts don't exist.
        - If we have no cuts and no API, we can still estimate cuts by
          converting density to API, and then API to cuts.
        - This is just a primitive test, so we do not evaluate the quantities,
          simply that some kind of value exists.
    '''
    if (oil.product_type is not None and
            oil.product_type.lower() == 'crude'):
        if (len(list(oil.cuts)) >= 3 or
                has_api_or_densities(oil)):
            return True  # cuts can be estimated if not present
        else:
            return False
    else:
        if len(list(oil.cuts)) >= 3:
            return True
        else:
            return False


def has_densities_below_pour_point(oil):
    '''
        This may be presumptuous, but I believe the volumetric coefficient
        that we use for calculating densities at temperature are probably for
        oils in the liquid phase.  So we would like to check if any
        densities in our oil fall below the pour point.

        Note: Right now we won't worry about estimating the pour point
              if the pour point data points don't exist for the record,
              then we will assume that our densities are probably fine.
    '''
    try:
        pp_max = oil.pour_point_max_k
        pp_min = oil.pour_point_min_k
        pour_point = min([pp for pp in (pp_min, pp_max) if pp is not None])
    except (ValueError, TypeError):
        pour_point = None

    if pour_point is None:
        return False
    else:
        rho_temps = [d.ref_temp_k for d in oil.densities
                     if d.ref_temp_k is not None]
        if oil.api is not None:
            rho_temps.append(288.15)

        if any([(t < pour_point) for t in rho_temps]):
            try:
                oil_id = oil.adios_oil_id
            except AttributeError:
                oil_id = oil.oil_id

            print('\toil_id: {}, pour_point: {}, rho_temps: {}, lt: {}'
                  .format(oil_id, pour_point, rho_temps,
                          [(t < pour_point) for t in rho_temps]))
            return True


def oil_api_matches_density(oil):
    '''
        The oil API should pretty closely match its density at 15C.

        Note: we will need to rework this function.  Return True for now.
    '''
    return True
