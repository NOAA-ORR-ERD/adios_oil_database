"""
version_update.py: Code for dealing with different versions of the data model

NOTE: this may need some refactoring when it gets more complicated
"""
from .version import Version, VersionError

from . import oil


class Updater:
    ver_from = None
    ver_to = None

    def __call__(self, py_json):
        this_ver = Version(py_json.get('adios_data_model_version'))

        if this_ver == self.ver_to:  # nothing to be done
            return py_json
        elif this_ver != self.ver_from:  # can't update this
            return py_json
        else:  # we can do the update
            self._version_check(py_json)

            py_json = self.update(py_json)
            py_json['adios_data_model_version'] = str(self.ver_to)

            return py_json

    def update(self, py_json):
        # do-nothing updater for only additions.
        return py_json

    def _version_check(self, py_json):
        # just in case
        this_ver = Version(py_json.get('adios_data_model_version'))

        if this_ver != self.ver_from:
            raise ValueError("Update called with JSON of wrong version"
                             f"JSON version: {this_ver}, this updater "
                             f"can update: {self.ver_from}")


class update_0_10_0_to_0_11_0(Updater):
    ver_from = Version(0, 10, 0)
    ver_to = Version(0, 11, 0)

    def update(self, py_json):
        # change the name of the fraction_weathered attribute
        if 'sub_samples' in py_json:  # very sparse records may not
            for ss in py_json['sub_samples']:
                md = ss['metadata']
                # note: this may add a fraction_weathered = None, but that's OK
                if 'fraction_weathered' in md:
                    # rename it
                    md['fraction_evaporated'] = md.get('fraction_weathered')
                    md.pop('fraction_weathered', None)

        # py_json['adios_data_model_version'] = str(self.ver_to)
        return py_json


class update_0_11_0_to_0_12_0(Updater):
    """
    an updater for only additions
    -- nothing to be done other than update the version
    """
    ver_from = Version(0, 11, 0)
    ver_to = Version(0, 12, 0)


# NOTE: updaters need to be in order
#       this could be automated it if gets unwieldy
UPDATERS = [update_0_10_0_to_0_11_0(),
            update_0_11_0_to_0_12_0(),
            ]


def update_json(py_json):
    """
    updates JSON for an oil object from an older version to a newer one
    """
    cur_ver = oil.ADIOS_DATA_MODEL_VERSION

    try:
        ver = Version(py_json['adios_data_model_version'])
    except KeyError:
        # assume it's the version from before we added a version
        ver = Version(0, 10, 0)
        py_json['adios_data_model_version'] = str(ver)

    if ver == cur_ver:  # nothing to be done
        return py_json

    # run it through the updaters
    for update in UPDATERS:
        py_json = update(py_json)

    # Now see if it worked
    ver = Version(py_json.get('adios_data_model_version'))

    if ver == cur_ver:
        return py_json

    elif ver > cur_ver:
        # try to see if it will load anyway -- auto-update.
        try:
            # update the version number and try to load it:
            py_json["adios_data_model_version"] = str(
                oil.ADIOS_DATA_MODEL_VERSION
            )

            this_oil = oil.Oil.from_py_json(py_json)

            # update (downgrade) the version number
            #   this may not be valid for the new version, as
            #   attributes may have been lost.

            return this_oil.py_json()
        except Exception:  # if anything goes wrong ....
            raise VersionError(f"Version: {ver} is not supported by "
                               "this version of the adios_db Oil object "
                               "-- you may need to update the adios_db "
                               "package.")
    else:
        raise VersionError(f"updater not available for version: {ver}")
