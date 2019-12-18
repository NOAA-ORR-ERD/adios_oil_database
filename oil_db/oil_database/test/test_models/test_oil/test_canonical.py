import pytest

from oil_database.models.oil import canonical

def test_get_new_oil():
    oil = canonical.get_new_oil("An Oil Name")
    assert oil["name"] == "An Oil Name"


def test_no_name():
    with pytest.raises(TypeError):
        oil = canonical.get_new_oil()
