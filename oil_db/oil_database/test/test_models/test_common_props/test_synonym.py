'''
    Test our Synonym model class
'''
from pydantic import ValidationError

from oil_database.models.common import Synonym

import pytest
pytestmark = pytest.mark.skipif(True, reason="Not using Synonyms now")


class TestSynonym():
    @pytest.mark.parametrize('name', [
        pytest.param(None,
                     marks=pytest.mark.raises(exception=ValidationError)),
        ('Synonym'),
    ])
    def test_init(self, name):
        if name is None:
            syn_obj = Synonym()
        else:
            syn_obj = Synonym(name=name)

        assert syn_obj.name == name
