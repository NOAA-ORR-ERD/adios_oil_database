#!/usr/bin/env python
import re
from functools import wraps
from datetime import datetime
import logging

from slugify import Slugify

custom_slugify = Slugify(to_lower=True, separator='_')

logger = logging.getLogger(__name__)


def join_with(separator):
    '''
        Class method decorator to join a list of labels with a separator
    '''
    def wrapper(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            return separator.join([i.strip()
                                   for i in func(self, *args, **kwargs)
                                   if i is not None])

        return wrapped

    return wrapper


def parse_time(func):
    '''
        Class method decorator to parse an attribute return value as a datetime

        Note: Apparently there are a few records that just don't have
              a sample date.  So we can't really enforce the presence
              of a date here.

        Note: The date formats are all over the place here.  So the default
              datetime parsing is not sufficient.
              Some formats that I have seen:
              - MM/DD/YYYY          # most common
              - MM-DD-YYYY          # different separator
              - DD/MM/YYYY          # 7 records very clearly in this format
              - MM/YYYY             # 3 records do this
              - YYYY                # 2 records do this
              - <month name>, YYYY  # 3 records do this
              So we will:
              - Treat MM/DD/YYYY as the default
              - Allow for DD/MM/YYYY if it can be clearly determined
              - Fix the others in the file.
    '''
    def parse_single_datetime(date_str):
        datetime_pattern = re.compile(
            r'(?P<month>\d{1,2})[-/](?P<day>\d{1,2})[-/](?P<year>\d{2,4})'
            r'(?:[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'  # Optional HH:mm
            r'(?::(?P<second>\d{1,2})'  # Optional seconds
            r'(?:\.(?P<microsecond>\d{1,6})0*)?)?)?'  # Optional microseconds
            r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?\Z'  # Optional timezone
        )

        if isinstance(date_str, datetime):
            return date_str
        elif isinstance(date_str, str):
            match = re.match(datetime_pattern, date_str.strip())

            if match is not None:
                tp = {k: int(v) for k, v in match.groupdict().items()
                      if v is not None}

                if tp['month'] > 12:
                    tp['month'], tp['day'] = tp['day'], tp['month']

                return datetime(**tp)
            else:
                raise ValueError('datetime "{}" is not parsable'
                                 .format(date_str))
        else:
            return None

    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret, (tuple, list, set, frozenset)):
            return [parse_single_datetime(dt) for dt in ret]
        else:
            return parse_single_datetime(ret)

    return wrapper


def date_only(func):
    def date_portion(date_time_obj):
        if isinstance(date_time_obj, datetime):
            return date_time_obj.strftime('%Y-%m-%d')
        else:
            return None

    def wrapper(*args, **kwargs):
        return date_portion(func(*args, **kwargs))

    return wrapper


class ParserBase(object):
    '''
        Only things that are common to all parsers
    '''
    def slugify(self, label):
        '''
            Generate a string that is suitable for use as an object attribute.
            - The strings will be snake-case, all lowercase words separated
              by underscores.
            - They will not start with a numeric digit.  If the original label
              starts with a digit, the slug will be prepended with an
              underscore ('_').

            Note: Some unicode characters are not intuitive.  Specifically,
                  In German orthography, the grapheme ß, called Eszett or
                  scharfes S (Sharp S).  It looks sorta like a capital B to
                  English readers, but converting it to 'ss' is not completely
                  inappropriate.
        '''
        if label is None:
            return label

        prefix = '_' if label[0].isdigit() else ''

        return prefix + custom_slugify(label)
