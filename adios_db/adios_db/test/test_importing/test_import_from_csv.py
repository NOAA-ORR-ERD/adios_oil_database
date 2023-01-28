"""
Tests the importing from a "NOAA Standard" CSV file script.

Note: tests aren't comprehensive, but at least there's something
    if it breaks on future files - please add a test!

"""
from pathlib import Path

from adios_db.models.oil.oil import ADIOS_DATA_MODEL_VERSION

from adios_db.scripts.import_csv import read_csv_file

test_file = Path(__file__).parent / "example_data" / "LSU_AlaskaNorthSlope.csv"

def test_read_csv():
    """
    one big honking test for the whole thing -- not ideal, but something
    """
    oil = read_csv_file(test_file)

    assert oil.adios_data_model_version == ADIOS_DATA_MODEL_VERSION

def test_metadata():
    """
    not really an isolated test, but at least errors will be a bit more specific
    """
    md = read_csv_file(test_file).metadata
    test_map = [
        ("name", "Alaska North Slope"),
        ("source_id", ""),
        ("location", ""),
        ("sample_date", "2011"),
        ("comments", "The data in this record may have been compiled from multiple sources and reflect samples of varying age and composition"),
        ("product_type", "Crude Oil NOS")
    ]

    for attr, value in test_map:
        assert getattr(md, attr) == value

    assert md.reference.year == 2011
    assert md.reference.reference == "Martin, J. (2011). Comparative toxicity and bioavailability of heavy fuel oils to fish using different exposure scenarios(Doctoral dissertation)."





