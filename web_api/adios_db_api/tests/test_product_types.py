"""
Functional tests for the product_types API
"""
from adios_db.models.oil.product_type import PRODUCT_TYPES

# NOTE: testapp coming from conftest.py


def test_get_product_types(testapp):
    testapp.get("/product-types", status=307)

    resp = testapp.get("/product-types/")

    result = resp.json_body
    product_types = result[0]['product_types']

    print(type(product_types))
    print(product_types)
    assert product_types == list(PRODUCT_TYPES)


def test_get_product_types_valid_id(testapp):
    # the only ID that is valid is 0
    resp = testapp.get("/product-types/0/")

    result = resp.json_body
    product_types = result['product_types']

    print(type(product_types))
    print(product_types)
    assert product_types == list(PRODUCT_TYPES)


def test_get_product_types_invalid_id(testapp):
    # the only ID that is valid is 0
    testapp.get("/product-types/1/", status=404)

    testapp.get("/product-types/bogus/", status=400)

    testapp.get("/product-types/1.1/", status=400)


def test_post(testapp):
    """
    should get an appropriate error
    """
    testapp.post_json("/product-types", params={"arbitrary": 'data'},
                      status=307)
    testapp.post_json("/product-types/", params={"arbitrary": 'data'},
                      status=405)


def test_put(testapp):
    """
    should get an appropriate error
    """
    testapp.put_json("/product-types", params={"arbitrary": 'data'},
                     status=307)
    testapp.put_json("/product-types/", params={"arbitrary": 'data'},
                     status=405)


def test_delete_bad_req(testapp):
    """
    should get an appropriate error
    """
    testapp.delete('/product-types', status=307)
    testapp.delete('/product-types/', status=405)
