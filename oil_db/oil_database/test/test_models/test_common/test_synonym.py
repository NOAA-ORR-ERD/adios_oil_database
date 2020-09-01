'''
    Test our Synonym model class
'''
import pytest

from oil_database.models.common import Synonym


class TestSynonym():
    @pytest.mark.parametrize('name', [
        pytest.param(None,
                     marks=pytest.mark.raises(exception=TypeError)),
        ('Synonym'),
    ])
    def test_init(self, name):
        if name is None:
            syn_obj = Synonym()
        else:
            syn_obj = Synonym(name=name)

        assert syn_obj.name == name
