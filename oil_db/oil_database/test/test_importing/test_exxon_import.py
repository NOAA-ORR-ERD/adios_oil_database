"""
tests of the Exxon data importer

no very complete, because then I'd be pretty much re-writing a
lot of it (Or writing it all by hand)

but still handy to have some tests to run the code while under development
"""
from pathlib import Path
from pprint import pprint

import pytest

from oil_database.data_sources.exxon_assays import (ExxonDataReader,
                                                    ExxonMapper,
                                                    ExxonRecordParser
                                                    )


example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"


def test_read_index():
    reader = ExxonDataReader(example_dir, example_index)

    assert reader.index is not None
    print(reader.index)
    assert reader.index == [('HOOPS Blend',
                             example_dir / 'Crude_Oil_HOOPS_Blend_assay_xls.xlsx'),
                            ]


def test_get_records():
    reader = ExxonDataReader(example_dir, example_index)

    records = reader.get_records()

    name, data = next(records)

    assert name == "HOOPS Blend"
    # some checking of the record
    assert data[5][0] == "HOOPS16F"
    # if more checks are needed: see next test

    # there should be only one
    with pytest.raises(StopIteration):
        next(records)


def test_read_excel_file():
    record = ExxonDataReader.read_excel_file(example_dir /
                                             "Crude_Oil_HOOPS_Blend_assay_xls.xlsx")

    pprint(record[:7])

    # there could be a LOT here, but just to make sure it isn't completely bonkers
    assert record[0][0] == "ExxonMobil"
    assert record


def test_ExxonRecordParser():
    """
    This is really a do-nothing function
    """
    assert ExxonRecordParser("something random") == "something random"


# This is where the real work happens!
def test_exxon_mapper():
    record = next(ExxonDataReader(example_dir, example_index).get_records())

    oil = ExxonMapper(record)


    assert oil.name == 'HOOPS Blend'
    assert oil.reference.startswith("ExxonMobil")

    print(oil)

#    assert False





