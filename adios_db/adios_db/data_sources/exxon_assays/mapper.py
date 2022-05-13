#!/usr/bin/env python
"""
Exxon Mapper Base

Not really a class -- it's really a function that build up an
oil object
"""
import logging
from .v1.mapper import ExxonMapperV1
from .v2.mapper import ExxonMapperV2

logger = logging.getLogger(__name__)


def ExxonMapper(record):
    """
    Accepts and Exxon record:

    tuple of:
      - oil name
      - list of lists of the spreadsheet contents

    returns an Oil Object
    """
    first_page = record[1][0]

    if (isinstance(first_page[8][1], str) and
            first_page[8][1].lower() == 'crude summary report'):
        logger.info('This is a new version Exxon document.')
        return ExxonMapperV2(record)
    else:
        return ExxonMapperV1(record)
