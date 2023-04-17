import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--mongo",
        action="store_true",
        default=False,
        help="run the tests that require mongo to be running"
    )


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "mongo: mark test as requiring mongo")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--mongo"):
        # --mongo given in cli: do not skip tests that require mongo
        return

    skip_mongo = pytest.mark.skip(reason="need --mongo option to run")

    for item in items:
        if "mongo" in item.keywords:
            item.add_marker(skip_mongo)
