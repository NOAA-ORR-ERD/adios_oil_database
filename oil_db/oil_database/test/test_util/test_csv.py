
import pytest

from oil_database.util.csv import (CSVFile, CSVFileWithHeader,
                                   FileHeaderLengthError)


@pytest.fixture(scope='session')
def csv_file(tmpdir_factory):
    '''
        Generate a simple test .csv file.  The fields will contain content
        referencing their row and column positions.
    '''
    fn = tmpdir_factory.mktemp('data').join('test.csv')

    with open(str(fn), 'wb') as fd:
        fd.write('00\t01\n'
                 '10\t11\n')

    return fn


@pytest.fixture(scope='session')
def csv_header_file(tmpdir_factory):
    '''
        Same as the simple .csv file, but with a header row.
    '''
    fn = tmpdir_factory.mktemp('data').join('test_header.csv')

    with open(str(fn), 'wb') as fd:
        fd.write('f1\tf2\n'
                 '00\t01\n'
                 '10\t11\n')

    return fn


@pytest.fixture(scope='session')
def csv_bad_header_file(tmpdir_factory):
    '''
        Same as the .csv file with header, but with a bad header row.
    '''
    fn = tmpdir_factory.mktemp('data').join('bad_header.csv')

    with open(str(fn), 'wb') as fd:
        fd.write('f1\tf2\n'
                 '00\t01\t02\n')

    return fn


class TestCSVFile(object):
    @pytest.mark.parametrize("name, delim",
                             [("test", None),
                              ("test", '|')
                              ])
    def test_init(self, name, delim):
        if delim is None:
            delim = '\t'  # expected default value
            csv_file = CSVFile('test')
        else:
            csv_file = CSVFile('test', delim)

        assert csv_file.name == name
        assert csv_file.field_delim == delim

    @pytest.mark.parametrize("delim, line, expected",
                             [('\t', '', None),
                              ('\t', '\n', [None]),
                              ('\t', u'\n', [None]),
                              ('\t', '\t', [None, None]),
                              ('\t', '\t\n', [None, None]),
                              ('\t', u'\t\n', [None, None]),
                              ('\t', ' ', [' ']),
                              ('\t', ' \n', [' ']),
                              ('\t', u' \n', [' ']),
                              ('\t', ' \t ', [' ',  ' ']),
                              ('\t', ' \t \n', [' ',  ' ']),
                              ('\t', '00\t01\n', ['00', '01']),
                              ('\t', 'f0\tf1', ['f0', 'f1']),
                              ('\t', 'f0\tf1\n', ['f0', 'f1']),
                              ('\t', u'f0\tf1\n', ['f0', 'f1']),
                              ('|', 'f0|f1', ['f0', 'f1']),
                              ('|', 'f0|f1\n', ['f0', 'f1']),
                              ('|', u'f0|f1\n', ['f0', 'f1']),
                              ])
    def test_parse_row(self, delim, line, expected):
        csv_obj = CSVFile('test', delim)

        res = csv_obj._parse_row(line)
        assert res == expected

    def test_csvfile_context(self, csv_file):
        '''
            Test our contextual functions by using our class in a context
            manager.
        '''
        with CSVFile(str(csv_file)) as csv_obj:
            rowcount = 0

            for l in csv_obj.readlines():
                for fieldcount, f in enumerate(l):
                    assert f.startswith(str(rowcount))
                    assert f.endswith(str(fieldcount))

                rowcount += 1

    def test_seek(self, csv_file):
        '''
            Test our seek method.  This api will not be directly used,
            generally speaking, but is used by other api functions.
            Nevertheless, we will test it.
        '''
        with CSVFile(str(csv_file)) as csv_obj:
            assert csv_obj.fileobj.tell() == 0
            csv_obj.seek(10)
            assert csv_obj.fileobj.tell() == 10

    def test_rewind(self, csv_file):
        '''
            Test our rewind method.
        '''
        with CSVFile(str(csv_file)) as csv_obj:
            csv_obj.seek(10)
            assert csv_obj.fileobj.tell() == 10

            csv_obj.rewind()
            assert csv_obj.fileobj.tell() == 0

    def test_write(self, csv_file):
        '''
            Test our write method.
        '''
        with CSVFile(str(csv_file)) as csv_obj:
            with pytest.raises(NotImplementedError):
                csv_obj.write()


class TestCSVFileWithHeader(object):
    def test_csvfile_context(self, csv_header_file):
        '''
            This is similar to a basic csv_file, but should handle a header
            row.
        '''
        with CSVFileWithHeader(str(csv_header_file)) as csv_obj:
            rowcount = 0

            for l in csv_obj.readlines():
                for fieldcount, f in enumerate(l):
                    assert f.startswith(str(rowcount))
                    assert f.endswith(str(fieldcount))

                rowcount += 1

    def test_rewind(self, csv_header_file):
        '''
            Test our rewind method.  After rewinding, we should be at the
            position of the first data row, skipping the header row.
        '''
        with CSVFileWithHeader(str(csv_header_file)) as csv_obj:
            curr_pos = csv_obj.fileobj.tell()

            csv_obj.seek(10)
            assert csv_obj.fileobj.tell() == 10

            csv_obj.rewind()
            assert csv_obj.fileobj.tell() == curr_pos

    def test_bad_header(self, csv_bad_header_file):
        '''
            This tests a header row that doesn't match the data fields.
        '''
        with CSVFileWithHeader(str(csv_bad_header_file)) as csv_obj:
            with pytest.raises(FileHeaderLengthError):
                csv_obj.readline()
