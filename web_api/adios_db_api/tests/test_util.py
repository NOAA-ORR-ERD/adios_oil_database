
import pytest

from bson.objectid import ObjectId
from adios_db_api.util import fix_bson_ids


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
def test_fix_bson_ids(obj, expected):
    fixed = fix_bson_ids(obj)

    assert fixed == expected