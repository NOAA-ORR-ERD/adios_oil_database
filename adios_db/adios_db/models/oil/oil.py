"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
import json

from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json

from ...computation.gnome_oil import make_gnome_oil

from .metadata import MetaData
from .sample import SampleList
from .version import Version

ADIOS_DATA_MODEL_VERSION = Version(0, 11, 0)

from .version_update import update_json  # noqa: E402

# from .validation.warnings import WARNINGS
from .validation.errors import ERRORS  # noqa: E402


@dataclass_to_json
@dataclass
class Oil:
    oil_id: str  # required
    adios_data_model_version: Version = ADIOS_DATA_MODEL_VERSION
    metadata: MetaData = field(default_factory=MetaData)
    sub_samples: SampleList = field(default_factory=SampleList)
    status: list = field(default_factory=list)
    permanent_warnings: list = field(default_factory=list)
    extra_data: dict = field(default_factory=dict)

    def __post_init__(self):
        '''
            Put any validation code here (__init__() is auto-generated by the
            dataclass decorator, and it will clobber any attempt to overload
            the __init__.)
        '''
        if self.oil_id == "":
            raise TypeError("You must supply a non-empty oil_id")
        elif not isinstance(self.oil_id, str):
            raise ValueError("oil_id must be a string")
        # arbitrary limit to catch ridiculous ones (UUIDs are 36 chars)
        self._validate_id(self.oil_id)

    def __str__(self):
        """
        need a custom str here, so we don't get a huge dump of the entire tree of data
        """
        return (f"{self.metadata.name}\n"
                f"ID: {self.oil_id}\n"
                f"Product Type: {self.metadata.product_type}"
                )

    @staticmethod
    def _pre_from_py_json(py_json):
        # update the JSON version
        py_json = update_json(py_json)

        # this all now done in the update_json method
        # ver = py_json.get('adios_data_model_version')
        # if Version.from_py_json(ver) != ADIOS_DATA_MODEL_VERSION:
        #     raise ValueError("Can't load this version of the data model")
        # py_json.pop('adios_data_model_version', None)
        return py_json

    @classmethod
    def from_file(cls, infile):
        """
        load an Oil object from the passed in JSON file

        it can be either a path or an open file object

        NOTE: this could be in the decorator -- but we only really need it
              for a full record.
        """
        try:
            py_json = json.load(infile)
        except AttributeError:
            # must not be an open file-like object
            py_json = json.load(open(infile, encoding='utf-8'))

        return cls.from_py_json(py_json)

    @staticmethod
    def _validate_id(id):
        if id == "":
            raise TypeError("You must supply a non-empty oil_id")
        elif not isinstance(id, str):
            raise ValueError("oil_id must be a string")
        # arbitrary limit to catch ridiculous onesL UUID is  36 characters
        elif len(id) > 40:
            raise ValueError("oil_id must be a string less than 40 characters in length")


    def validate(self):
        """
        validation specific to the Oil object itself

        validation of sub-objects is automatically applied
        """
        # see if it can be used as a GNOME oil
        # NOTE: this is an odd one, as it puts the information in a different place
        try:
            make_gnome_oil(self)
            self.metadata.gnome_suitable = True
        # if any other kind of Error -- it will raise.
        except (ValueError, IndexError):
            self.metadata.gnome_suitable = False
        msgs = []

        # Validate ID
        try:
            self._validate_id(self.oil_id)
        except ValueError:
            msgs.append(ERRORS["E001"].format(self.oil_id))
        # always add these:
        msgs.extend("W000: " + m for m in self.permanent_warnings)
        return msgs

    def reset_validation(self):
        """
        calls the validate method, and updates the status with the result
        """
        msgs = self.validate()
        self.status = list(set(msgs))

    def to_file(self, outfile, sparse=True):
        """
        save an Oil object as JSON to the passed in file

        it can be either a path or a writable open file object

        NOTE: this could be in the decorator -- but we only really need it
              for a full record.
        """
        try:
            json.dump(self.py_json(sparse=sparse), outfile)
        except AttributeError:
            # must not be an open file-like object
            with open(outfile, 'w', encoding='utf-8') as outfile:
                json.dump(self.py_json(sparse=sparse), outfile, indent=4)

        return None





