'''
    Test our Category model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.common import Category


class TestCategory():
    @pytest.mark.parametrize('name, parent',
                             [
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 'Parent',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ('Category', None),
                              ('Category', 'Parent'),
                              ])
    def test_init(self, name, parent):
        if name is None and parent is None:
            cat_obj = Category()
        elif parent is None:
            cat_obj = Category(name=name)
        elif name is None:
            cat_obj = Category(parent={'name': parent})
        else:
            cat_obj = Category(name=name, parent={'name': parent})

        assert cat_obj.name == name

        if parent is not None:
            assert cat_obj.parent.name == parent

    @pytest.mark.parametrize('children',
                             [
                              None,
                              ['child'],
                              ['Child 1', 'Child 2'],
                              ])
    def test_init_children(self, children):
        if children is None:
            cat_obj = Category(name='Category')
        else:
            cat_obj = Category(name='Category',
                               children=[{"name": c} for c in children])

        if children is None:
            assert cat_obj.children == []
        else:
            assert [c.name for c in cat_obj.children] == children
