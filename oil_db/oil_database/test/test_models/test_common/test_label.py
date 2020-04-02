'''
Test our Category model class

NOTE: This may be all obsolete -- we aren't doing hierarchtical catagories
      anymore

And the Catagory model depends on mongo -- so these are skipped most of the
time anyway
'''


import pytest

from pydantic import ValidationError

from oil_database.models.common import Label

from ..conftest import db_setup


Label.attach(db_setup().db)


class TestLabel():
    @pytest.mark.parametrize('name', [
        pytest.param(None,
                     marks=pytest.mark.raises(exception=ValidationError)),
        ('Category'),
    ])
    def test_init(self, name):
        if name is None:
            cat_obj = Label()
        else:
            cat_obj = Label(name=name)

        assert cat_obj.name == name
