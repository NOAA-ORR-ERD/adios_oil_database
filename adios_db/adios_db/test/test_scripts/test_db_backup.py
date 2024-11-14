"""
Test the db_backup script.

You need fully set up mongodb for this to be tested properly

so at this point, all it does is test one function :-(

"""

from pathlib import Path
import json
import pytest

from adios_db.models.oil.oil import Oil

try:
    import bson
except ImportError:
    pytest.skip("pymongo is needed to run these tests",
                allow_module_level=True)


HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output_data"

TEST_DATA_DIR = (HERE.parent
                 / "data_for_testing" / "noaa-oil-data" / "oil")
EXAMPLE_DATA_DIR = HERE.parent / "data_for_testing" / "example_data"

print(TEST_DATA_DIR)

BIG_RECORD = json.load(open(TEST_DATA_DIR / "EC" / "EC02234.json",
                            encoding="utf-8"))



# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost
# pytestmark = pytest.mark.skipif(True, reason="not working yet" )
#pytestmark = pytest.mark.mongo


# @pytest.mark.skip("needs to be finished before turning on")
# def test_backup_script():
#     # so it won't try to import if skipped
#     from adios_db.scripts import db_backup

#     settings = default_settings()
#     base_path = ""

#     db_backup.backup_db(settings, base_path)

#     assert False

def test_db_backup_export_to_file():
    """
    tests the export to file code itself, without mongo.
    """
    from adios_db.scripts.db_backup import export_to_file
    record = BIG_RECORD

    old_oil = Oil.from_py_json(record)
    # change something to ensure an error
    old_oil.metadata.API = 12.0
    # add the validation
    old_oil.status = ['E043: An example error message']
    old_oil.metadata.gnome_suitable = False
    record = old_oil.py_json()

    export_to_file(record, OUTPUT_DIR, collection_name='oil')

    expected_path = OUTPUT_DIR / "oil" / "EC" / "EC02234.json"

    new_oil = Oil.from_file(expected_path)

    assert new_oil.status == []
    assert new_oil.metadata.gnome_suitable is None



