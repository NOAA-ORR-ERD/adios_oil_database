"""
Functional tests for the product_types API

"""

import pytest
from webtest.app import AppError

from oil_database.models.oil.values import PRODUCT_TYPES

# NOTE: testapp coming from conftest.py


def test_get_product_types(testapp):
    resp = testapp.get("/product_types")

    result = resp.json_body
    print(type(result))
    print(result)

    assert result == list(PRODUCT_TYPES)


def test_post(testapp):
    """
    should get an error with a post attempt
    """
    with pytest.raises(AppError):
        testapp.post_json("/product_types", params={"arbitrary": 'data'})


def test_put(testapp):
    """
    should get an error with a put attempt
    """
    with pytest.raises(AppError):
        testapp.put_json("/product_types", params={"arbitrary": 'data'})


def test_delete_bad_req(testapp):
    with pytest.raises(AppError):
        testapp.delete('/product_types', status=400)
