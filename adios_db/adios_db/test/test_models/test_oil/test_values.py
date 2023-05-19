from adios_db.models.oil.values import Reference


def test_Reference():
    ref = Reference(year=2013)
    ref.reference = ('Barker, C.H. 2013. "An Arbitrary Title". Journal '
                     'of Nonsense.Seattle, WA. Vol. 13 No. 3 pp. 123-125')

    assert ref.year == 2013


def test_Reference_json():
    ref = Reference(year=2013)
    ref.reference = ('Barker, C.H. 2013. "An Arbitrary Title". Journal '
                     'of Nonsense.Seattle, WA. Vol. 13 No. 3 pp. 123-125')

    py_json = ref.py_json()
    assert py_json['year'] == 2013

    ref2 = Reference.from_py_json(py_json)
    assert ref2.year == 2013
    assert "Barker, C.H." in ref2.reference

    assert ref == ref2
