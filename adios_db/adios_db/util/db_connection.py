import logging

from ..session import Session

logger = logging.getLogger(__name__)


def connect_mongodb(settings):
    """
    We are using MongoDB via pymongo for our database
    """
    host = settings['mongodb.host']
    port = int(settings['mongodb.port'])
    database = settings['mongodb.database']

    return Session(host=host, port=port, database=database)
