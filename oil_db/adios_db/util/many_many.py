"""
ManyMany

class for managing a many to many relationship in a pair of dicts

The two mappings are "left" and "right"

The left one is originally populated by the initializer.

After that they are equivalent -- when you add something to one the other is updated.

Currently there is no way to remove anything

YOu can access copies of the mappings with:

``ManyMany.left``
and
``ManyMany.right``

They are copies, so that mutating them won't break the internal data.

"""

from collections import defaultdict

import copy

class ManyMany:

    def __init__(self, initial_data=None):
        """
        initialize a ManyMany structure

        :param initial_data: initial data for the left dict. of the form:
                             {key1: iterable_of_values,
                              key2: iterable_of_values,
                              ...
                              }

        all values must be hashable
        """

        self._left_dict = {key: set(values) for key, values in initial_data.items()}
        self._rebuild_right()

        self._lefthash = self._dict_hash(self._left_dict)
        self._righthash = self._dict_hash(self._right_dict)

    def _rebuild_right(self):
        """
        rebuilds the right dict to match the left
        """
        self._right_dict = self._rebuild(self._left_dict)

    def _rebuild_left(self):
        """
        rebuilds the left dict to match the right
        """
        self._left_dict = self._rebuild(self._right_dict)

    @staticmethod
    def _rebuild(source):
        """
        builds a "reversed" dict from a source dict
        """
        new = {}
        for key, values in source.items():
            for val in values:
                new.setdefault(val, set()).add(key)
        return new

    @staticmethod
    def _dict_hash(d):
        """
        Provide a hash of a dict with a sequence of hashable items as the values

        This was to be used to know if an internal dict was changed,
          but it turns out that's not useful (at least not in a robust way)
        """
        hashable = frozenset({k: frozenset(v) for k, v in d.items()}.items())
        return hash(hashable)

    def add_to_left(self, key, value):
        """
        add a new value to the left dict

        :param key: the key the value is to be added to
        :param value: the value to be added

        If the key is already there, the value will be added to the corresponding set

        A new key and set will be created if it is not already there.
        """
        self._left_dict.setdefault(key, set()).add(value)
        self._rebuild_right()

    def add_to_right(self, key, value):
        """
        add a new value to the right dict

        :param key: the key the value is to be added to
        :param value: the value to be added

        If the key is already there, the value will be added to the corresponding set

        A new key and set will be created if it is not already there.
        """
        self._right_dict.setdefault(key, set()).add(value)
        self._rebuild_left()

    @property
    def left(self):
        """
        A copy of the left dict

        It's a copy, so it won't change the internal ones if mutated
        """
        return copy.deepcopy(self._left_dict)

    @property
    def right(self):
        """
        A copy of the right dict

        It's a copy, so it won't change the internal ones if mutated
        """
        return copy.deepcopy(self._right_dict)


# ################
# tests
# ###############$


# some data to use for tests:
data = {'this': ('the', 'other', 'thing'),
        'that': ('the', 'and', 'some', 'more', 'thing'),
        'them': ('the', 'and', 'some')
        }


def test_initialize():
    mm = ManyMany(data)

    print(mm.left)
    assert mm.left['this'] == set(data['this'])
    assert mm.left['them'] == set(data['them'])


def test_right():
    mm = ManyMany(data)

    assert mm.right['some'] == set(['that', 'them'])
    assert mm.right['and'] == set(['that', 'them'])
    assert mm.right['other'] == set(['this'])


def test_rebuild_orig():

    mm = ManyMany(data)

    old_left = copy.deepcopy(mm.left)
    print(mm.left)

    mm._rebuild_left()
    print(mm.left)

    assert mm.left == old_left


def test_add_to_left_new():
    mm = ManyMany(data)

    mm.add_to_left('those', 'newthing')

    left = mm.left
    right = mm.right

    print(left)
    print(right)

    assert 'those' in left
    assert left['those'] == {'newthing'}
    assert 'newthing' in right
    assert right['newthing'] == {'those'}


def test_add_to_left_existing():
    mm = ManyMany(data)

    mm.add_to_left('this', 'newthing')

    left = mm.left
    right = mm.right

    print(left)
    print(right)

    assert 'newthing' in left['this']
    assert 'newthing' in right
    assert right['newthing'] == {'this'}


def test_add_to_right_new():
    mm = ManyMany(data)

    mm.add_to_right('newthing', 'those')

    left = mm.left
    right = mm.right

    print(left)
    print(right)

    assert 'those' in left
    assert left['those'] == {'newthing'}
    assert 'newthing' in right
    assert right['newthing'] == {'those'}



def test_dict_hash():
    """
    make sure you can hash it!

    and that adding something changes the hash
    """
    # dict with a set of strings as keys
    d = {key: set(values) for key, values in data.items()}

    h1 = ManyMany._dict_hash(d)
    print(h1)

    # add something to a value
    d['this'].add('newone')
    h2 = ManyMany._dict_hash(d)

    assert h1 != h2




