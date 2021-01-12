import pytest

from bson.objectid import ObjectId

from adios_db.util.json import (fix_bson_ids,
                                    json_to_bson_obj_id,
                                    ObjFromDict)


class TestBson(object):
    @pytest.mark.parametrize('obj, expected',
                             [
                              (ObjectId(b'123456789012'),
                               '313233343536373839303132'),
                              ({'id': ObjectId(b'123456789012')},
                               {'id': '313233343536373839303132'}),
                              ([ObjectId(b'123456789012')],
                               ['313233343536373839303132']),
                              ({ObjectId(b'123456789012')},
                               {'313233343536373839303132'}),
                              ({'ids': [ObjectId(b'123456789012')]},
                               {'ids': ['313233343536373839303132']}),
                              ({'ids': (ObjectId(b'123456789012'))},
                               {'ids': ('313233343536373839303132')}),
                              ({'ids': {ObjectId(b'123456789012')}},
                               {'ids': {'313233343536373839303132'}}),
                              ])
    def test_fix_bson_ids(self, obj, expected):
        fixed = fix_bson_ids(obj)

        assert fixed == expected

    @pytest.mark.parametrize('obj, expected',
                             [
                              ({'_id': '313233343536373839303132'},
                               {'_id': ObjectId('313233343536373839303132')}),
                              ])
    def test_json_to_bson_obj_id(self, obj, expected):
        json_to_bson_obj_id(obj)

        assert obj == expected


class TestObjFromDict(object):
    def test_obj_from_dict(self):
        obj = ObjFromDict({'_id': '1234'})

        assert hasattr(obj, '_id')
        assert obj._id == '1234'

    def test_recurse_dict(self):
        obj = ObjFromDict({'dict_attr': {'_id': '1234'}
                           })

        assert hasattr(obj, 'dict_attr')
        assert hasattr(obj.dict_attr, '_id')
        assert obj.dict_attr._id == '1234'

    def test_recurse_list(self):
        obj = ObjFromDict({'list_attr': [{'_id': '1234'}]
                           })

        assert hasattr(obj, 'list_attr')
        assert isinstance(obj.list_attr, list)
        assert hasattr(obj.list_attr[0], '_id')
        assert obj.list_attr[0]._id == '1234'

    def test_recurse_tuple(self):
        obj = ObjFromDict({'tuple_attr': ({'_id': '1234'},)
                           })

        assert hasattr(obj, 'tuple_attr')
        assert isinstance(obj.tuple_attr, tuple)
        assert hasattr(obj.tuple_attr[0], '_id')
        assert obj.tuple_attr[0]._id == '1234'

    def test_recurse_set(self):
        '''
            Note: sets cannot contain mutable elements like dictionaries or
                  lists, and we will not try to make it do more than Python
                  supports.
        '''
        obj = ObjFromDict({'set_attr': {'1234'}})

        assert hasattr(obj, 'set_attr')
        assert isinstance(obj.set_attr, set)

        assert '1234' in obj.set_attr

    def test_recurse_frozenset(self):
        '''
            Note: sets cannot contain mutable elements like dictionaries or
                  lists, and we will not try to make it do more than Python
                  supports.
        '''
        obj = ObjFromDict({'frozenset_attr': frozenset(('1234',))})

        assert hasattr(obj, 'frozenset_attr')
        assert isinstance(obj.frozenset_attr, frozenset)

        assert '1234' in obj.frozenset_attr

    def test_top_level_list_fail(self):
        '''
            The top level JSON structure needs to be a dictionary.
        '''
        with pytest.raises(ValueError):
            ObjFromDict(['1234'])

    def test_top_level_tuple_fail(self):
        '''
            The top level JSON structure needs to be a dictionary.
        '''
        with pytest.raises(ValueError):
            ObjFromDict(('1234',))

    def test_top_level_set_fail(self):
        '''
            The top level JSON structure needs to be a dictionary.
        '''
        with pytest.raises(ValueError):
            ObjFromDict({('1234',)})

    def test_top_level_frozenset_fail(self):
        '''
            The top level JSON structure needs to be a dictionary.
        '''
        with pytest.raises(ValueError):
            ObjFromDict(frozenset(('1234',)))
