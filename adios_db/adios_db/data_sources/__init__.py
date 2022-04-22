"""
Collection of file readers
"""
try:
    from slugify import Slugify
    field_name_sluggify = Slugify(to_lower=True, separator='_')
except ImportError:
    print("You need the awesome-slugify package to run the importing code")
    field_name_sluggify = None

from .reader import CsvFile
