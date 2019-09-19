import logging

from pymongo import MongoClient

logger = logging.getLogger(__name__)


def connect_mongodb(settings):
    '''
        We are using MongoDB via pymongo for our database
    '''
    host = settings['mongodb.host']
    port = settings['mongodb.port']

    return MongoClient(host=host, port=port)
