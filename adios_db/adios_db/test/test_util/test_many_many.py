import copy

from adios_db.util.many_many import ManyMany


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

    print(f'left: {left}, right: {right}')

    assert 'those' in left
    assert left['those'] == {'newthing'}
    assert 'newthing' in right
    assert right['newthing'] == {'those'}


def test_add_to_left_existing():
    mm = ManyMany(data)

    mm.add_to_left('this', 'newthing')

    left = mm.left
    right = mm.right

    print(f'left: {left}, right: {right}')

    assert 'newthing' in left['this']
    assert 'newthing' in right
    assert right['newthing'] == {'this'}


def test_add_to_right_new():
    mm = ManyMany(data)

    mm.add_to_right('newthing', 'those')

    left = mm.left
    right = mm.right

    print(f'left: {left}, right: {right}')

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
