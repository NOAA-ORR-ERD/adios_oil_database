"""
versions.py

Code for dealing with different versions of the data model
"""
from .oil import ADIOS_DATA_MODEL_VERSION


def update_json(py_json):
    """
    Updates JSON for an oil object from an older version to a newer one
    """
    cur_ver = ADIOS_DATA_MODEL_VERSION
    ver = py_json.get('adios_data_model_version')

    if ver is None:
        # assume it's the version from before we added a version
        ver = "0.10.0"

    ver = Version.from_py_json(ver)
    if ver == cur_ver:
        return py_json  # nothing to be done
    elif ver > cur_ver:
        raise VersionError(f"Version: {ver} is not supported "
                           "by this version of Oil object")
    else:
        raise VersionError(f"updater not available for version: {ver}")
