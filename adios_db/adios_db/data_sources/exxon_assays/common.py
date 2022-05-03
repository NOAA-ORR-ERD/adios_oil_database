import re


def next_id():
    """
    Generate the next oil record identifier
    """
    if not hasattr(next_id, 'count'):
        next_id.count = 0
    next_id.count += 1

    return next_id.count


def norm(string):
    """
    normalizes a string for comparing

    so far: lower case, whitespace strip
    trailing and leading comma strip
    """
    return string.strip().strip(',').strip(':').lower()


# Utilities:
def next_non_empty(data):
    while True:
        row = next(data)

        if not is_empty(row):
            break

    return row


def is_empty(row):
    return all([f is None for f in row])


def get_next_properties_row(data, exp_field):
    row = next_non_empty(data)

    if norm(row[0]) != norm(exp_field):
        raise ValueError(f'Something wrong with data sheet: {row}, '
                         f'expected: {exp_field}')

    return row


def to_number(field):
    """
    Try to extract a number from a text field.  Within this scope, we
    don't care to try extract any unit information, just the number.
    Some variations on numeric data fields in the Exxon Assays:
    - '1000F+'
    - '1000F'
    - '650'
    - 'C5' is not numeric
    """
    try:
        return float(field)
    except Exception:
        pass

    try:
        return float(re.search('^[0-9\\.]+', field).group(0))
    except Exception:
        pass

    return field
