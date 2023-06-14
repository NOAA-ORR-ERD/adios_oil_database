"""
tests for the LocationCoordinates object
"""
import pytest

from adios_db.models.oil.location_coordinates import LocationCoordinates


def test_point_good():
    P = LocationCoordinates(type="Point",
                            coordinates=(1.2, -3.2))

    assert P.type == "Point"
    assert tuple(P.coordinates) == (1.2, -3.2)


@pytest.mark.parametrize('coords', [
    # bad point
    (1, 2, 3),
    (1),
    [(3, 4)],
    [[(3, 4)]],
    (34, "this"),
    "th",
])
def test_bad_point(coords):
    with pytest.raises(ValueError):
        _P = LocationCoordinates(type="Point", coordinates=coords)


def test_polygon_good():
    coords = [[(1.2, -3.2), (1.3, -3.1), (1.1, -3.4), (1.2, -3.2)]]
    P = LocationCoordinates(type="Polygon", coordinates=coords)

    assert P.type == "Polygon"
    assert P.coordinates == coords


@pytest.mark.parametrize('coords', [
    # bad point
    [[(1.2, -3.2), (1.3,), (1.1, -3.4), (1.2, -3.2)]],
    # too_few_points
    [[(1.2, -3.2), (1.3, -3.1), (1.1, -3.4)]],
    # endpoints_not_match
    [[(1.2, -3.2), (1.3, -3.1), (1.1, -3.4), (1.3, -3.1)]],
])
def test_bad_polygon(coords):
    with pytest.raises(ValueError):
        _P = LocationCoordinates(type="Polygon", coordinates=coords)


def test_bad_geometry_type():
    with pytest.raises(ValueError):
        _P = LocationCoordinates(type="Something", coordinates=[])


def test_poly_to_json():
    coords = [[(1.2, -3.2), (1.3, -3.1), (1.1, -3.4), (1.2, -3.2)]]
    P = LocationCoordinates(type="Polygon", coordinates=coords)

    pyjs = P.py_json()

    print(pyjs)
    assert pyjs['type'] == "Polygon"
    assert pyjs['coordinates'] == coords


def test_poly_json_round_trip():
    coords = [[(1.2, -3.2), (1.3, -3.1), (1.1, -3.4), (1.2, -3.2)]]
    P = LocationCoordinates(type="Polygon", coordinates=coords)

    pyjs = P.py_json()
    print(pyjs)

    P2 = LocationCoordinates.from_py_json(pyjs)

    assert P2 == P


def test_point_json_round_trip():
    coords = (1.3, -3.1)
    P = LocationCoordinates(type="Point", coordinates=coords)

    pyjs = P.py_json()
    print(pyjs)

    P2 = LocationCoordinates.from_py_json(pyjs)

    assert P2 == P
