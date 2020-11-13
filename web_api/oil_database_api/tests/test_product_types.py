"""
Functional tests for the product_types API

"""

# import pytest
# from webtest.app import AppError

from oil_database.models.oil.product_type import PRODUCT_TYPES

# NOTE: testapp coming from conftest.py


def test_get_product_types(testapp):
    resp = testapp.get("/product-types")

    result = resp.json_body
    product_types = result[0]['product_types']

    print(type(product_types))
    print(product_types)
    assert product_types == list(PRODUCT_TYPES)


def test_post(testapp):
    """
    should get an error 405 Method Not Allowed
    """
    testapp.post_json("/product-types", params={"arbitrary": 'data'},
                      status=405)


def test_put(testapp):
    """
    should get an error 405 Method Not Allowed
    """
    testapp.put_json("/product-types", params={"arbitrary": 'data'},
                     status=405)


def test_delete_bad_req(testapp):
    """
    should get an error 405 Method Not Allowed
    """
    testapp.delete('/product-types', status=405)
