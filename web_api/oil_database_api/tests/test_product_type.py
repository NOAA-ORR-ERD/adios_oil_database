"""
Functional tests for the product_types API

"""

import pytest
import oil_database

# NOTE: testapp coming from conftest.py


def test_get_product_types(testapp):
    resp = testapp.get("/product_types")
    print(resp)
    print(resp.json_body)

    assert False


def test_post(testapp):
    """
    should get an error with a post attempt
    """
    testapp.post_json("/product_types", params={"arbitrary": 'data'})


def test_put(testapp):
    """
    should get an error with a put attempt
    """
    testapp.put_json("/product_types", params={"arbitrary": 'data'})


def test_delete_bad_req(testapp):
    testapp.delete('/product_types', status=400)
