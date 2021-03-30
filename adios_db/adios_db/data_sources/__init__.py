"""
Collection of file readers

Some common constants, etc. here
"""
from slugify import Slugify

from .reader import CsvFile


field_name_sluggify = Slugify(to_lower=True, separator='_')
