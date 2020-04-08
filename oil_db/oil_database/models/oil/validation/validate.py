"""
Validation of a single oil record


Currently, this is essentially a placeholder, so we have something to use
in the client.  It does about as little as it can, while still working

The top-level interface is a single function:

validate(pyjson_of_an_oil_record)

(pyjson is a python dict that is a match for the JSON)

It will add the validation messages to the "status" field of the record.


Currently, it converts the pyjson into a .oil/Oil object, then validates
on that.


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
# Putting these all here so we can keep track more easily
from .warnings import WARNINGS
from .errors import ERRORS


pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


def validate(oil_json):
    """
    validate the oil record.

    validation messages are added to the status field of the record

    :param oil: The oil record to be validated, in json-compatible python
                data structure.

    """
    try:
        oil = Oil.from_py_json(oil_json)
    except TypeError as err:
        if "argument: 'name'" in err.args[0]:
            oil_json["status"] = ERRORS["E001"]
            return
        else:  # some other TypeError
            raise

    messages = set()

    # first call Oil Object's validate
    messages.update(oil.validate())

    # then the stand-alone ones
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
    api = oil.API
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
    if not oil.sub_samples:
        return ERRORS["E003"]


def val_check_for_densities(oil):
    # note: would be good to be smart about temp densities are at
    if not oil.sub_samples:
        return WARNINGS["W006"]

    if (oil.sub_samples[0].physical_properties is None or
            oil.sub_samples[0].physical_properties.densities is None):
        return WARNINGS["W006"]

    return None


def val_check_for_distillation_cuts(oil):
    try:
        sample = oil.sub_samples[0]
    except (AttributeError, IndexError):
        return None

    try:
        if not sample.distillation_data:
            return WARNINGS["W007"]
    except AttributeError:
        return WARNINGS["W007"]
    return None


# build a list of all the validators:

VALIDATORS = [val for name, val in vars().items() if name.startswith("val_")]


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









