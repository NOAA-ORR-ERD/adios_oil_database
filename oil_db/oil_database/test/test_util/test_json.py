import pytest

from bson.objectid import ObjectId

from oil_database.util.json import fix_bson_ids, json_to_bson_obj_id


class TestBson(object):
    @pytest.mark.parametrize('obj, expected',
                             [
                              (ObjectId('123456789012'),
                               '313233343536373839303132'),
                              ({'id': ObjectId('123456789012')},
                               {'id': '313233343536373839303132'}),
                              ([ObjectId('123456789012')],
                               ['313233343536373839303132']),
                              ({ObjectId('123456789012')},
                               {'313233343536373839303132'}),
                              ({'ids': [ObjectId('123456789012')]},
                               {'ids': ['313233343536373839303132']}),
                              ({'ids': (ObjectId('123456789012'))},
                               {'ids': ('313233343536373839303132')}),
                              ({'ids': {ObjectId('123456789012')}},
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
