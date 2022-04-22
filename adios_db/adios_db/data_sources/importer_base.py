#!/usr/bin/env python
from functools import wraps
from datetime import datetime
import logging


try:
    from slugify import Slugify
    custom_slugify = Slugify(to_lower=True, separator='_')
except ImportError:
    print("You need the awesome-slugify package to run the importing code")
    custom_slugify = None

from dateutil import parser
from itertools import zip_longest
from builtins import isinstance


logger = logging.getLogger(__name__)


def join_with(separator):
    """
    Class method decorator to join a list of labels with a separator
    """
    def wrapper(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            return separator.join([i.strip()
                                   for i in func(self, *args, **kwargs)
                                   if i is not None])

        return wrapped

    return wrapper


def parse_time(func):
    """
    Class method decorator to parse an attribute return value as a datetime

    Note: Apparently there are a few records that just don't have
          a sample date.  So we can't really enforce the presence
          of a date here.

    Note: The April 2020 Env Canada datasheet has much more consistent
          date formats, but there are still some variations.
          Some formats that I have seen:
          - YYYY-MM-DD          # most common
          - YYYY                # 2 records
          - YYYY-MM             # 5 records

          Fortunately, dateutil will handle these without problems
    """
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret, (tuple, list, set, frozenset)):
            return [parse_single_datetime(dt) for dt in ret]
        else:
            return parse_single_datetime(ret)

    return wrapper


def parse_single_datetime(date_str):
    if isinstance(date_str, datetime):
        return date_str
    elif isinstance(date_str, int) and date_str < 3600:
        # it is unlikely that we've chosen a unix time within the first hour
        # of 01/01/1970.  It is probably a year value.
        return datetime(date_str, 1, 1, 0, 0)
    elif isinstance(date_str, str):
        return parser.parse(date_str, default=datetime(1970, 1, 1, 0, 0))
    else:
        return None


def date_only(func):
    def date_portion(date_time_obj):
        if isinstance(date_time_obj, datetime):
            return date_time_obj.strftime('%Y-%m-%d')
        else:
            return None

    def wrapper(*args, **kwargs):
        return date_portion(func(*args, **kwargs))

    return wrapper


class ImporterBase(object):
    """
    Only things that are common to all importer modules
    """
    def slugify(self, label):
        """
        Generate a string that is suitable for use as an object attribute.

        - The strings will be snake-case, all lowercase words separated
          by underscores.
        - They will not start with a numeric digit.  If the original label
          starts with a digit, the slug will be prepended with an
          underscore ('_').

        **Note:** Some unicode characters are not intuitive.  Specifically,
        In German orthography, the grapheme ß, called Eszett or
        scharfes S (Sharp S).  It looks sorta like a capital B to
        English readers, but converting it to 'ss' is not completely
        inappropriate.
        """
        if label is None:
            return label

        prefix = '_' if label[0].isdigit() else ''

        return prefix + custom_slugify(label)

    def deep_get(self, obj, attr_path, default=None):
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        attrs = attr_path

        try:
            for p in attrs:
                try:
                    p = int(p)
                except Exception:
                    pass

                obj = obj[p]

            return obj
        except KeyError:
            return default

    def deep_set(self, obj, attr_path, value):
        """
        Navigate a period ('.') delimited path of attribute values into the
        oil data structure and set a value at that location in the
        structure.

        Example paths:

        ``sub_samples.0.metadata.sample_id``  (sub_samples is assumed to be
        a list, and we go to the zero index for that part)

        ``physical_properties.densities.-1``  (densities is assumed to be a
        list, goes to the last item)

        ``physical_properties.densities.+``   (appends an item to the
        densities list and goes to that part.  the index value
        is assumed to be -1 in this case)
        """
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        for p, next_p in zip_longest(attr_path[:-1], attr_path[1:]):
            if (next_p is not None and
                    (self.is_int(next_p) or next_p == '+')):
                path_value_to_generate = []
            else:
                path_value_to_generate = {}

            if p == '+':
                obj.append(None)
                p = -1

            if self.is_int(p):
                p_int = int(p)

                idx_size = abs(p_int) + 1 if p_int >= 0 else abs(p_int)
                if idx_size > len(obj):
                    obj += [None] * (idx_size - len(obj))

                if obj[p_int] is None:
                    obj[p_int] = path_value_to_generate
            else:
                if p not in obj:
                    obj[p] = path_value_to_generate

            if self.is_int(p):
                obj = obj[int(p)]
            else:
                obj = obj[p]

        attr_path, attr = attr_path[:-1], attr_path[-1]

        if attr == '+':
            obj.append(None)
            attr = -1

        obj[attr] = value

    def is_int(self, value):
        try:
            int(value)
            return True
        except Exception:
            return False
