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


# Putting these all here so we can keep track more easily
# from .warnings import WARNINGS
from .errors import ERRORS

logger = logging.getLogger(__name__)


def validate_json(oil_json):
    """
    validate a json-compatible-python record

    An Oil object is returned, if it's possible to do so.

    The "status" field is updated in place, with no other alterations of the record
    """

    try:
        oil = Oil.from_py_json(oil_json)
    except TypeError as err:
        if "argument: 'oil_id'" in err.args[0]:
            oil_json["status"] = ERRORS["E001"]
            raise TypeError(ERRORS["E001"])
        else:
            raise

    validate(oil)

    return oil


def validate(oil):
    """
    validate an Oil object

    oil.status is updated in place
    """

    messages = set()

    # first call Oil Object's validate
    messages.update(oil.validate())

    # # then the stand-alone ones
    # for val_fun in VALIDATORS:
    #     msg = val_fun(oil)
    #     if msg:
    #         messages.add(msg)

    # set the oil status
    oil.status = list(messages)


# def validate(oil):
#     """
#     validate the oil record.

#     validation messages are added to the status field of the record

#     :param oil: The oil record to be validated, as an Oil object or
#                 in json-compatible python data structure.

#     """
#     if isinstance(oil, Oil):
#         validate_oil(oil)
#     else:
#         validate_json(oil)


# def val_has_reasonable_name(oil):
#     """
#     right now, reasonable is more than 5 characters

#     we may want to add more later
#     """
#     if len(oil.metadata.name.strip()) < 5:
#         return WARNINGS["W001"].format(oil.metadata.name)
#     else:
#         return None


# def val_has_product_type(oil):
#     '''
#     Oil records should have a product type
#     '''
#     valid_types = ('crude',
#                    'refined',
#                    'bitumen product',
#                    'other')

#     if not oil.metadata.product_type:
#         return WARNINGS["W002"]
#     elif not oil.metadata.product_type.lower() in ('crude',
#                                                    'refined',
#                                                    'bitumen product',
#                                                    'other'):
#         return WARNINGS["W003"].format(oil.metadata.product_type, valid_types)
#     else:
#         return None


# def val_check_api(oil):
#     api = oil.metadata.API
#     ptype = oil.metadata.product_type
#     if api is None:
#         if ptype in DOESNT_NEED_API:
#             return WARNINGS["W004"]
#         else:
#             return ERRORS["E002"]
#     if not (-60.0 < api < 100):  # somewhat arbitrary limits
#         return WARNINGS["W005"].format(api=api)


# def val_check_for_samples(oil):
#     if not oil.sub_samples:
#         return ERRORS["E003"]


# def val_check_for_densities(oil):
#     # note: would be good to be smart about temp densities are at
#     if not oil.sub_samples:
#         return WARNINGS["W006"]

#     if (oil.sub_samples[0].physical_properties is None or
#             oil.sub_samples[0].physical_properties.densities is None):
#         return WARNINGS["W006"]

#     return None


# def val_check_for_distillation_cuts(oil):
#     try:
#         sample = oil.sub_samples[0]
#     except (AttributeError, IndexError):
#         return None

#     try:
#         if not sample.distillation_data.cuts:
#             return WARNINGS['W007']
#     except AttributeError:
#         return WARNINGS['W007']
#     return None


# # build a list of all the validators:

# VALIDATORS = [val for name, val in vars().items() if name.startswith("val_")]
