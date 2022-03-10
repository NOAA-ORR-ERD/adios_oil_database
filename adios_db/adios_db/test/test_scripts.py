"""
test the various scripts

These don't test whether they work right, but should at least check that they
will run without errors
"""

from pathlib import Path
import pytest

from adios_db.scripts import db_backup


# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost
# pytestmark = pytest.mark.skipif(True, reason="not working yet" )

pytestmark = pytest.mark.mongo

HERE = Path(__file__).parent

OUTPUT_DIR = HERE / "output_data"


@pytest.mark.skip("needs to be finished before turning on")
def test_backup_script():
    settings = default_settings()
    base_path = ""
    db_backup.backup_db(settings, base_path)

    assert False


