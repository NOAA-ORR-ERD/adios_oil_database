"""
cleanup classes that work with density
"""
from adios_db.models.oil.cleanup import Cleanup, ALL_CLEANUPS, CLEANUP_MAPPING


def test_ALL_CLEANUPS():
    print(ALL_CLEANUPS)

    assert len(ALL_CLEANUPS) == len(CLEANUP_MAPPING)

    for obj in ALL_CLEANUPS:
        assert issubclass(obj, Cleanup)

    for ID, obj in CLEANUP_MAPPING.items():
        assert ID == obj.ID
