"""
test the various scripts

These don't test whether they work right, but should at least check that they
will run without errors
"""

from pathlib import Path
import pytest

# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost
# pytestmark = pytest.mark.skipif(True, reason="not working yet" )

pytestmark = pytest.mark.mongo

try:
    import bson
except ImportError:
    pytest.skip("pymongo is needed to run these tests", allow_module_level=True)


HERE = Path(__file__).parent

OUTPUT_DIR = HERE / "output_data"

@pytest.mark.skip("needs to be finished before turning on")
def test_backup_script():
    # so it won't try to import if skipped
    from adios_db.scripts import db_backup
    settings = default_settings()
    base_path = ""
    db_backup.backup_db(settings, base_path)

    assert False

