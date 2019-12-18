import pytest

from oil_database.models.oil import canonical

def test_get_new_oil():
    oil = canonical.get_new_oil("An Oil Name")
    assert oil["name"] == "An Oil Name"


def test_no_name():
    with pytest.raises(TypeError):
        oil = canonical.get_new_oil()

@pytest.mark.xfail
def test_get_sparse_oil():
    """
    try getting a sparse version of the oil

    should only have the minimum fields
    """
    oil = canonical.get_new_oil("An Oil Name", sparse=True)

