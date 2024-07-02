"""
tests of the Environment Canada data import modules

As complete as possible, because we want to test for correctness,
and we also want to document how it works.
Either we test it correctly, or we test it in an episodic manner on the
real dataset.
"""
from pathlib import Path

import pytest

from adios_db.data_sources import CsvFile

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing

example_dir = Path(__file__).resolve().parent / 'example_data'
data_file = example_dir / 'CsvTestSet.csv'


class TestBaseCsvFile:
    def test_init(self):
        with pytest.raises(TypeError):
            _reader = CsvFile()

    def test_init_nonexistant_file(self):
        with pytest.raises(FileNotFoundError):
            _reader = CsvFile('bogus.file')

    def test_init_with_valid_file(self):
        reader = CsvFile(data_file)

        assert reader.name == data_file
        assert len(reader.field_names) == 4

        # Let's just check some of the individual category/field combinations
        assert reader.field_names.index('Field1') == 0
        assert reader.field_names.index('Field4') == 3

    def test_readlines(self):
        reader = CsvFile(data_file)
        recs = list(reader.readlines())

        assert len(recs) == 4

        for rec in recs:
            assert len(rec) == 4

    def test_rewind(self):
        reader = CsvFile(data_file)
        recs = list(reader.readlines())

        assert len(recs) == 4

        for rec in recs:
            assert len(rec.keys()) == 4

        reader.rewind()
        recs = list(reader.readlines())

        assert len(recs) == 4

        for rec in recs:
            assert len(rec.keys()) == 4

    @pytest.mark.parametrize('value, expected', [
        ('string', 'str'),
        ('5', 'int'),
        ('5.0', 'float'),
        ('5.5', 'float'),
    ])
    def test_convert_fields(self, value, expected):
        reader = CsvFile(data_file)

        converted = reader.convert_field(value)
        print(f'{value} converted to {converted}')

        assert type(converted).__name__ == expected
