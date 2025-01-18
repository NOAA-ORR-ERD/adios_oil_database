
import datetime


class EnumValidator:
    """
    validator for Enum values: a value that can only be one of a set

    """
    def __init__(self, valid_items, err_msg, case_insensitive=False):
        """
        :param valid_items: list of valid items -- can be anything that an `in`
                            test will work for.
        :param err_msg: The error message that should be used on failure.
                        Should be a format string that takes two parameters:
                        item and valid_items

        :param case_insensitive=False: whether you want the test to be
                                       case-insensitive.
                                       Only works for string values, of course.

        Note: It is possible to pass in a set() type for our valid items.
              This has a non-obvious side effect on the messages we generate
              in that the order of the items is not guaranteed from one run
              to the next.
              This can cause a lot of churn in the noaa-oil-data project,
              as a new commit triggers a validation process, which can
              potentially update the status messages for any record in the
              repo.  And any change in a record will trigger a new commit.
              So it has been observed that a set, even a small one with only
              two items, will alternate its items back and forth, generating
              a *bunch* of redundant commits.
              So it would be best here if we ensured our valid_items has a
              consistent order.
        """
        if case_insensitive:
            valid_items = sorted([item.lower() for item in valid_items])
        else:
            valid_items = sorted(valid_items)

        self.valid_items = valid_items
        self.err_msg = err_msg
        self.case_insensitive = case_insensitive

    def __call__(self, item):
        if self.case_insensitive:
            try:
                item = item.lower()
            except AttributeError:
                pass  # so non-strings will fail the in test, but not crash.

        if item not in self.valid_items:
            return [self.err_msg.format(item, self.valid_items)]
        else:
            return []


class FloatRangeValidator:
    """
    Validator for float values that can only be a given range

    range is inclusive (<= and >=)
    """
    def __init__(self, min_value, max_value, err_msg=None):
        """
        :param min: minimum value allowed

        :param max: maximum value allowed

        :param err_msg: The error message that should be used on failure.
                        Should be a format string that takes three parameters:
                        default is:
                            "ValidationError: {} is not between {} and {}"
        """
        self.min = min_value
        self.max = max_value

        if err_msg is None:
            self.err_msg = "ValidationError: {} is not between {} and {}"
        else:
            self.err_msg = err_msg

    def __call__(self, value):
        try:
            value = float(value)
        except ValueError:
            return [self.err_msg.format(value, self.min, self.max)]

        if not self.min <= value <= self.max:
            return [self.err_msg.format(value, self.min, self.max)]
        else:
            return []


class YearValidator:
    """
    Validator for float values that can only be a given range

    range is inclusive (<= and >=)
    """
    def __init__(self, min_year, max_year, err_msg=None):
        """
        :param min: minimum year allowed

        :param max: maximum year allowed

        :param err_msg: The error message that should be used on failure.
                        Should be a format string that takes three parameters:
                        default is:
                            "ValidationError: {} is not between {} and {}"
        """
        self.min = min_year
        self.max = max_year

        if err_msg is None:
            self.err_msg = ("ValidationError: {} is not a year "
                            "between {} and {}")
        else:
            self.err_msg = err_msg

    def __call__(self, value):
        try:
            value = int(value)
        except ValueError:
            return [self.err_msg.format(value, self.min, self.max)]

        if not self.min <= value <= self.max:
            return [self.err_msg.format(value, self.min, self.max)]
        else:
            return []


class DateTimeValidator:
    """
    Validator for strings that should be an ISO string, e.g.

    2010-06-24T

    it uses the build-in:
    datetime.fromisoformat()

    so anything that passes that will pass this validator

    """
    def __init__(self, err_msg=None):
        """
        :param err_msg: The error message that should be used on failure.
                        Should be a format string that takes one parameter:
                        default is:

                        "ValidationError: {} is not a valid datetime string"
        """
        if err_msg is None:
            self.err_msg = 'ValidationError: "{}"" is not a valid datetime string: {}'
        else:
            self.err_msg = err_msg

    def __call__(self, value):
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError as err:
            return [self.err_msg.format(value, err)]
        return []
