'''
Test our Category model class
'''
import pytest
pytestmark = pytest.mark.skipif(True, reason="Not using Catagories now")


from pydantic import ValidationError

from oil_database.models.common import Category

from ..conftest import db_setup

Category.attach(db_setup().db)


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
        parent_obj = None

        if name is None and parent is None:
            cat_obj = Category()
        elif parent is None:
            cat_obj = Category(name=name)
        elif name is None:
            parent_obj = Category(name=parent).save()
            cat_obj = Category(parent=parent_obj._id).save()
        else:
            parent_obj = Category(name=parent).save()
            cat_obj = Category(name=name, parent=parent_obj._id)

        assert cat_obj.name == name

        if parent_obj is not None:
            assert parent_obj.name == parent
            assert cat_obj.parent == parent_obj._id

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
                               children=[Category(name=c).save()._id
                                         for c in children])

        if children is None:
            assert cat_obj.children == []
        else:
            assert [Category.find_one({'_id': c}).name
                    for c in cat_obj.children] == children












