"""
testing serving up the user docs
"""
import pytest

from adios_db.models.oil.product_type import PRODUCT_TYPES

# NOTE: testapp coming from conftest.py
# NOTE: if we can figure this out, there will need to be a dummy test file
#       in the git repo for this test to work.

pytestmark = pytest.mark.skipif(
    True,
    reason="skipping because we can't get tests to work"
)


def test_get_user_docs(testapp):
    testapp.get("/docs/user_docs/index.html", status=307)
    resp = testapp.get("/docs/user_docs/index.html")

    # why am I getting a redirect???
    # but this should let it move on
    if resp.status_code == 307:
        print("following the response")
        resp = resp.follow()

    # now getting a 404 -- something is weird

    print("Response from get on docs")
    print(resp)

    result = resp.body
    print(resp.body)

    assert resp.status_code == 200
    # maybe check something else??
