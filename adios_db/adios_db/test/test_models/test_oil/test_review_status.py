import pytest

from adios_db.models.oil.review_status import ReviewStatus


def test_init_empty():
    rs = ReviewStatus()

    assert rs.status == "Not Reviewed"
    assert rs.reviewers == ""
    assert rs.review_date == ""
    assert rs.notes == ""


def test_json_empty():
    rs = ReviewStatus()
    js = rs.py_json()

    print(js)

    assert js == {'status': 'Not Reviewed'}


def test_set_everything():
    rs = ReviewStatus()

    rs.status = "Review Complete"
    rs.reviewers = "Peter, Paul, and Mary"
    rs.review_date = "2021-08-09"
    rs.notes = "This is a meaningless note."

    js = rs.py_json()

    print(js)

    assert js == {
        'status': 'Review Complete',
        'reviewers': 'Peter, Paul, and Mary',
        'review_date': '2021-08-09',
        'notes': 'This is a meaningless note.'
    }


@pytest.mark.parametrize('status', ["Not Reviewed",
                                    "Under Review",
                                    "Review Complete"])
def test_validation_good(status):
    rs = ReviewStatus()

    rs.status = status

    msgs = rs.validate()

    assert not msgs


def test_validation_bad():
    rs = ReviewStatus()

    rs.status = "Bad Status"

    msgs = rs.validate()

    assert "E013" in msgs[0]


def test_validation_date_good():
    rs = ReviewStatus()

    rs.status = "Review Complete"
    rs.reviewers = "Peter, Paul, and Mary"
    rs.review_date = "2021-08-09"
    rs.notes = "This is a meaningless note."

    msgs = rs.validate()

    assert not msgs


def test_validation_date_bad():
    rs = ReviewStatus()

    rs.status = "Review Complete"
    rs.reviewers = "Peter, Paul, and Mary"
    rs.review_date = "2021-35-09"
    rs.notes = "This is a meaningless note."

    msgs = rs.validate()

    assert len(msgs) == 1
    assert 'W011' in msgs[0]
