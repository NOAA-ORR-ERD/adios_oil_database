"""
tests of the Exxon data importer

no very complete, because then I'd be pretty much re-writing a
lot of it (Or writing it all by hand)

but still handy to have some tests to run the code while under development
"""

from pathlib import Path

from oil_database.data_sources.exxon_assays import ExxonDataReader


example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"


def test_reader_init():
    reader = ExxonDataReader(example_dir, example_index)

    assert reader.index == []
    for rec in reader.get_records():
        print(rec)

