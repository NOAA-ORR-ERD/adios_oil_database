"""
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
"""
import logging

from adios_db.models.oil.product_type import types_to_labels

logger = logging.getLogger(__name__)


def load_labels(db):
    for name, product_types in types_to_labels.right.items():
        db.label.insert_one({'name': name,
                             'product_types': list(product_types)})


def print_all_labels(db):
    logger.info('Labels in the database...')

    for label in db.label.find({}):
        logger.info(f'\t{label["name"]}')
