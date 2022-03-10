#!/usr/bin/env python
import logging

from .importer_base import ImporterBase

logger = logging.getLogger(__name__)


class ParserBase(ImporterBase):
    """
    Only things that are common to all parsers
    """
    def __init__(self, values):
        self.src_values = values
        self.oil_obj = {}
