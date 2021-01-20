"""
Collection of file readers

Some common constants, etc. here
"""
from slugify import Slugify


field_name_sluggify = Slugify(to_lower=True, separator='_')