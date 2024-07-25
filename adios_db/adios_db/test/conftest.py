
from pathlib import Path
import pytest


TEST_DATA_DIR = Path(__file__).parent / "data_for_testing"

def pytest_addoption(parser):
    parser.addoption(
        "--mongo",
        action="store_true",
        default=False,
        help="run the tests that require mongo to be running"
    )
    parser.addoption(
        "--import",
        action="store_true",
        default=False,
        help="run the importing tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "mongo: mark test as requiring mongo")
    config.addinivalue_line("markers",
                            "importing: mark test as being an import test")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--mongo"):
        # --mongo not given in cli: skip tests that require mongo

        skip_mongo = pytest.mark.skip(reason="need --mongo option to run")

        for item in items:
            if "mongo" in item.keywords:
                item.add_marker(skip_mongo)

    if not config.getoption("--import"):
        # --import not given in cli: skip import tests

        skip_import = pytest.mark.skip(reason="need --import option to run")

        for item in items:
            if "importing" in item.keywords:
                item.add_marker(skip_import)


