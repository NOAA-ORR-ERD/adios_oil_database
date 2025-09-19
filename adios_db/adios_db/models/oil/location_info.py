"""
place to hold location related code

right now, a bit of normalization, but maybe in the future, we'll put more here

"""

from .validation.warnings import WARNINGS

# Can't think of any way other than hard coding this list:
countries = {
 'Mauritius',
 'Australia',
 'Denmark',
 'New Zealand',
 'Colombia',
 'Mexico',
 'Argentina',
 'Germany',
 'Venezuela',
 'Qatar',
 'Canada',
 'Libya',
 'Norway',
 'Japan',
 'Brazil',
 'UK',
 'Zaire',
# 'Hong Kong',
 'Indonesia',
 'Angola',
 'Iran',
 'United Kingdom',
 'Iraq',
 'China',
 'the Netherlands',
 'Saudi Arabia',
 'Singapore',
 'South Korea',
 'Nigeria',
 'Egypt',
 'USA',
 'United Arab Emirates',
}

def validate_location(location):
    msgs = []
    splitup = location.split(", ", maxsplit=1)
    # special case Singapore -- if we find other city states we can generalize this
    if location == "Singapore, Singapore":
        return msgs
    if len(splitup) == 2 and splitup[0] in countries:
        should_be = ", ".join((splitup[1], splitup[0]))
        msgs.append(WARNINGS['W012'].format(location, should_be))
    return msgs



