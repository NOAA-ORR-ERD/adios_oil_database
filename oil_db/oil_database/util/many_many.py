"""
ManyMany

class for managing a many to many relationship in a pair of dicts

There is one "Primary" mapping, with the second one kept in sync


"""

from collections import defaultdict


class ManyMany:

    def __init__(self, initial_data=None):
        """
        initialize with a ManyMany structure

        :param initial_data: initial data for the primary dict. of teh form:
                             {key: [sequence of values]}
        """

        self.primary_dict = {key: set(values) for key, values in initial_data.items()}
        self.rebuild_secondary()

    def rebuild_secondary(self):
        sec = {}
        for key, values in self.primary_dict.items():
            for val in values:
                sec.setdefault(val, set()).add(key)

        self.secondary_dict = sec

    @property
    def primary(self):
        return self.primary_dict

    @property
    def secondary(self):
        return self.secondary_dict


# some data to use for tests:
data = {'this': ['the', 'other', 'thing'],
        'that': ['the', 'and', 'some', 'more', 'thing'],
        'them': ['the', 'and', 'some']
        }


def test_initialize():
    mm = ManyMany(data)

    print(mm.primary)
    assert mm.primary['this'] == set(data['this'])
    assert mm.primary['them'] == set(data['them'])


def test_secondary():
    mm = ManyMany(data)

    assert mm.secondary['some'] == set(['that', 'them'])
    assert mm.secondary['and'] == set(['that', 'them'])
    assert mm.secondary['other'] == set(['this'])
