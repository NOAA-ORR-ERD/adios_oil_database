'''
Test our Label model class
'''
import pytest

from adios_db.models.common import Label


class TestLabel():
    @pytest.mark.parametrize('name', [
        pytest.param(None,
                     marks=pytest.mark.raises(exception=TypeError)),
        ('Label'),
    ])
    def test_init(self, name):
        if name is None:
            cat_obj = Label()
        else:
            cat_obj = Label(name=name)

        assert cat_obj.name == name
