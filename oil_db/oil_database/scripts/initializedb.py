import logging


from oil_database.db_init.imported_record import add_imported_records
from oil_database.db_init.env_canada_record import add_ec_records
from oil_database.db_init.exxon_record import add_exxon_records

from oil_database.db_init.oil import process_oils
from oil_database.db_init.categories import process_categories

logger = logging.getLogger(__name__)


def load_db(settings):
    '''
        We will assume the connect() has already happened prior to this
        function.
    '''
    add_all_imported_records(settings)

    process_oils()

    process_categories(settings)


def add_all_imported_records(settings):
    '''
        Note: we will probably want a more modular, pluggable, method for
              managing our data sources in the future.
    '''
    #add_imported_records(settings)
    add_ec_records(settings)
    # add_exxon_records(settings)
