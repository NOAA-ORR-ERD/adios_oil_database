from pathlib import Path

from adios_db.data_sources.noaa_csv.reader import read_csv


HERE = Path(__file__).parent
sample_file = HERE / "example_data" / "example_noaa_csv.csv"


def test_load():
    """
    test weather the whole thing loads

    This isn't really unit testing, but I'm lazy right now :-(
    """
    oil = read_csv(sample_file)

    assert oil.metadata.name == "DMA, Chevron -- 2021"
    assert oil.metadata.API == 36.5
    assert oil.metadata.source_id == "xx-123"
    assert oil.metadata.alternate_names == ["Fred", "Bob"]
    assert oil.metadata.location == "California"

    assert oil.metadata.reference.year == 2021
    assert oil.metadata.reference.reference == 'Barker, C.H. 2021. "A CSV file reader for the ADIOS Oil Database."'
