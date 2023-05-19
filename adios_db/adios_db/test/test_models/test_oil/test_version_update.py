"""
tests of the version updating code

not much here -- probably should be more careful!
"""
from pathlib import Path

from adios_db.models.oil import oil
from adios_db.models.oil.version import VersionError

import pytest


HERE = Path(__file__).parent
DATADIR = HERE / "../../data_for_testing/example_data/"


def test_new_version_still_works():
    """
    If we try to create an Oil object from a JSON file that is newer
    than the code, it should try to read it anyway, and only fail if it
    can't read it.

    high_version_file.json has an ridiculously high version number
     -- but is a version 0.12.0 file
    """
    this_oil = oil.Oil.from_file(DATADIR / "high_version_file.json")

    # make sure version wasn't changed
    assert this_oil.adios_data_model_version == oil.ADIOS_DATA_MODEL_VERSION

    # just to make sure something loaded
    assert this_oil.metadata.name == "Cook Inlet [2003]"


def test_newer_version_cant_load():
    """
    if we try to create an Oil object from a JSON file that is newer than
    the code version, it should fail if it can't make an Oil out of it.

    high_version_changed.json has an ridiculously high version number
     -- and the metadata.labels field has been changes so it won't load.
    """
    with pytest.raises(VersionError):
        _o = oil.Oil.from_file(DATADIR / "high_version_changed.json")
